import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.cluster import AgglomerativeClustering
from collections import Counter
import uuid
from database import db_service
import asyncio

async def process_and_cluster(df):
    df['hobbies'] = df['hobbies'].apply(lambda x: x.split(','))
    df['topics'] = df['topics'].apply(lambda x: x.split(','))

    unique_hobbies = set(hobby.strip() for sublist in df['hobbies'] for hobby in sublist)
    unique_topics = set(topic.strip() for sublist in df['topics'] for topic in sublist)

    for hobby in unique_hobbies:
        df[hobby] = df['hobbies'].apply(lambda x: 1 if hobby in [h.strip() for h in x] else 0)
    for topic in unique_topics:
        df[topic] = df['topics'].apply(lambda x: 1 if topic in [t.strip() for t in x] else 0)

    df = pd.get_dummies(df, columns=['gender', 'year'], drop_first=True)
    df.drop(['hobbies', 'topics'], axis=1, inplace=True)

    # Make sure we have enough data to create clusters
    if len(df) < 5:
        print("Not enough data for clustering. Minimum 5 entries required.")
        return df
        
    hobbies_distances = euclidean_distances(df[list(unique_hobbies)])
    topics_distances = euclidean_distances(df[list(unique_topics)])
    df['hobbies_similarity'] = 1 / (1 + hobbies_distances.mean(axis=1))
    df['topics_similarity'] = 1 / (1 + topics_distances.mean(axis=1))
    df['combined_similarity'] = (df['hobbies_similarity'] + df['topics_similarity']) / 2

    clustering_data = df.drop(columns=['email', 'purpose', 'hobbies_similarity', 'topics_similarity', 'combined_similarity'])
    
    # Calculate number of groups (1 group per 5 people, minimum 1)
    num_groups = max(1, len(df) // 5)
    agg_cluster = AgglomerativeClustering(n_clusters=num_groups, affinity='euclidean', linkage='ward')
    df['cluster'] = agg_cluster.fit_predict(clustering_data)

    return adjust_group_sizes(df, min_size=4, max_size=6)

def adjust_group_sizes(df, min_size=4, max_size=6):
    from random import choice
    group_sizes = Counter(df['cluster'])
    small_groups = [group for group, size in group_sizes.items() if size < min_size]
    large_groups = [group for group, size in group_sizes.items() if size > max_size]

    for group in large_groups:
        while group_sizes[group] > max_size:
            individual_index = choice(df[df['cluster'] == group].index)
            if small_groups:
                new_group = choice(small_groups)
                df.at[individual_index, 'cluster'] = new_group
                group_sizes[group] -= 1
                group_sizes[new_group] += 1
            else:
                break  # No small groups to transfer to

    return df

def extract_clusters(df):
    clusters = df['cluster'].unique()
    grouped_data = []
    for cluster in clusters:
        group_name = f'Group {cluster + 1}'
        members = df[df['cluster'] == cluster]['email'].tolist()
        grouped_data.append({
            'id': str(uuid.uuid4()),
            'group_name': group_name,
            'email': ','.join(members)
        })
    return grouped_data

async def run_clustering():
    try:
        # Get questionnaire data from PostgreSQL
        questionnaire_data = await db_service.get_questionnaire_data()
        if not questionnaire_data:
            print("No questionnaire data found")
            return

        # Convert to DataFrame
        df = pd.DataFrame(questionnaire_data)
        
        # Process and cluster
        clustered_df = await process_and_cluster(df)
        
        # If we have cluster data (might not if insufficient data)
        if 'cluster' in clustered_df.columns:
            groups = extract_clusters(clustered_df)
            # Save groups to PostgreSQL
            await db_service.save_groups(groups)
            print("Clustering completed successfully")
        else:
            print("Clustering skipped - not enough data")
            
    except Exception as e:
        print(f"Error during clustering: {str(e)}")
        raise

async def schedule_clustering():
    while True:
        await run_clustering()
        await asyncio.sleep(24 * 60 * 60)  # Run every 24 hours

if __name__ == "__main__":
    asyncio.run(schedule_clustering())


