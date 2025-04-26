from plombery import register_pipeline, task, Trigger
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import BaseModel
import logging
from utils.db import check_if_processed, mark_as_processed
from utils.llm_analyzer import analyze_content_with_llm
from utils.rss_fetcher import get_new_substack_posts
from utils.kafka_producer import publish_to_kafka


# Input Params : Passing as it isn't needed.
class PipelineParams(BaseModel):
    # Add parameters if needed (e.g., min_words)
    pass

# Step 1: Fetching new RSS posts.
@task
def fetch_posts(params: PipelineParams):
    posts = get_new_substack_posts()
    logging.info(f"Fetched {len(posts)} posts.")
    return posts

# Step 2: Filtering already processed posts.
@task
def filter_new(posts):
    new_posts = []
    for post in posts:
        url = post.get('post_url')
        timestamp = post.get('timestamp')
        if not timestamp:
            logging.warning(f"Skipping post with invalid timestamp: {post['post_title']}")
            continue
        if check_if_processed(url):
            logging.info(f"Already processed: {post['post_title']}")
            continue
        new_posts.append(post)
    logging.info(f"{len(new_posts)} new posts to process.")
    return new_posts

# Step 3: Analyzing posts using LLM [Mocked Scenario].
@task
def analyze_posts(posts):
    analyzed_posts = []
    for post in posts:
        # Ensure post content is not empty or invalid
        if not post.get('post_content'):
            logging.warning(f"Skipping post with empty content: {post['post_title']}")
            continue
        
        # Analyze content using LLM
        logging.info(f"Analyzing post: {post['post_title']}")
        analysis = analyze_content_with_llm(post['post_content'])
        
        # If analysis is empty, log a warning
        if not analysis:
            logging.warning(f"No analysis returned for post: {post['post_title']}")
        
        if 'analysis' not in post:
            logging.warning(f"No analysis found for: {post['post_title']}")
        else:
            logging.info(f"Analysis exists for: {post['post_title']}")


        # Store analysis result in the post data
        post['analysis'] = analysis
        
        # Add post to analyzed_posts list
        analyzed_posts.append(post)

        # Debugging log to check analysis
        logging.debug(f"Analysis for {post['post_title']}: {analysis}")
        print(f"Analysis for {post['post_title']}: {analysis}")

    
    return analyzed_posts


# Step 4: Marking processed and publishing to Kafka.
@task
def publish_and_mark(posts):
    for post in posts:
        try:
            post_data = {
                'post_title': post['post_title'],
                'post_url': post['post_url'],
                'timestamp': post['timestamp'],
                'content': post['post_content'],
                'analysis': post['analysis']
            }
            publish_to_kafka('processed_substack_articles', post_data)
            mark_as_processed(post['post_url'], post['timestamp'])
            logging.info(f"Processed and published: {post['post_title']}")
        except Exception as e:
            logging.error(f"Failed to process post {post['post_url']}: {e}")

# Registering the pipeline flow.
register_pipeline(
    id="substack_pipeline",
    name="Substack RSS LLM Pipeline",
    description="Extracts new Substack articles, analyzes with LLM, and publishes to Kafka.",
    params=PipelineParams,
    tasks=[
        fetch_posts,
        filter_new,
        analyze_posts,
        publish_and_mark
    ],
    triggers=[
        Trigger(
            id="midnight_daily",
            name="Midnight Daily",
            description="Run every night at midnight to fetch and process new articles",
            params=PipelineParams(),  # Add parameters if needed
            schedule=IntervalTrigger(days=1),
        )
    ],
)
