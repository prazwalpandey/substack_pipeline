# substack_pipeline

## Introduction

The purpose of this POC is to design and implement a multi-stage data pipeline, encompassing data extraction(and cleaning), enrichment via AI analysis, and publishing. This task
simulates a real-world scenario involving gathering information from substack publications
(like https://robertreich.substack.com/about and https://www.publicnotice.co/), processing
it, and making it available for downstream systems through Kafka topic.

## Objectives

1. Monitors a defined set of Substack publications(2).
2. Poll at certain interval to get the data(Every Midnight).
3. Extracts key information and content from these new posts.
4. Analyzes the extracted article content using an AI model (LLM) to identify key topics
and associated sentiment per topic(Mocked Sentiment Analysis).
5. Publishes the combined extracted and analyzed data to a streaming platform (Kafka
topic).

## Substack Publications Monitored

Chose on the basis of popularity and daily updates.
1. Robert Reich RSS Feed → https://robertreich.substack.com/feed
2. Public Notice RSS Feed → https://www.publicnotice.co/feed

## Tools

• Python : Program Source Code  
• Plombery : Orchestration Tool  
• Kafka : Publishing Message to Kafka Topic  
• Docker : Kafka Containerization  
• Feedparser, BeautifulSoup, html, re, emoji : Clean Text Parising  
• PostgreSQL : Persistent Storage(Marks and Checks Already Processed)  

## File Structuring

substack/  
  utils/ # Utility folder for modules  
      __init__.py # Package initialization  
      db.py # Database utility  
      kafka_producer.py # Kafka producer utility  
      llm_analyzer.py # LLM analyzer utility  
      rss_fetcher.py # RSS fetcher utility  
  docker-compose.yml # Docker Compose configuration file  
  main.py # Main entry point of the application  
  pipeline.py # Defines the pipeline logic  
  requirements.txt # Python dependencies  

## Pipeline Implementation
