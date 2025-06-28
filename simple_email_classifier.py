#!/usr/bin/env python3
"""
Simplified Email Classification System

A streamlined version focusing on core email classification functionality
with comprehensive logging and error handling.
"""

import logging
import sys
import time
from typing import List, Dict, Any
from pathlib import Path

import pandas as pd
from openai import OpenAI

def setup_logging() -> logging.Logger:
    """Set up comprehensive logging for the email classifier."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger("email_classifier")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "email_classification.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info("Logging system initialized")
    return logger

# Initialize logging
logger = setup_logging()

class EmailClassifier:
    """
    Email classification system using OpenAI GPT for categorizing customer emails.
    """
    
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o"):
        """
        Initialize the email classifier.
        
        Args:
            api_key (str): OpenAI API key
            base_url (str, optional): Custom API base URL
            model (str): Model name to use for classification
        """
        self.model = model
        self.valid_categories = ["order", "inquiry", "other"]
        self.default_category = "other"
        
        logger.info("Initializing EmailClassifier...")
        logger.debug(f"Model: {model}")
        
        try:
            # Initialize OpenAI client
            client_params = {"api_key": api_key}
            if base_url:
                client_params["base_url"] = base_url
                logger.debug(f"Using custom base URL: {base_url}")
            
            self.client = OpenAI(**client_params)
            
            # Test connection
            logger.debug("Testing OpenAI connection...")
            test_response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def classify_single_email(self, subject: str, body: str) -> str:
        """
        Classify a single email into predefined categories.
        
        Args:
            subject (str): Email subject line
            body (str): Email body content
            
        Returns:
            str: Classification category
        """
        # Input validation and sanitization
        subject = str(subject) if subject is not None else ""
        body = str(body) if body is not None else ""
        
        # Truncate if too long
        if len(subject) > 200:
            subject = subject[:200] + "..."
            logger.debug("Truncated long subject line")
        
        if len(body) > 2000:
            body = body[:2000] + "..."
            logger.debug("Truncated long email body")
        
        # Create classification prompt
        prompt = self._create_classification_prompt(subject, body)
        
        try:
            logger.debug(f"Classifying email: '{subject[:50]}...'")
            
            # Make API request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1,
                top_p=1.0
            )
            
            # Extract and validate response
            category = response.choices[0].message.content.strip().lower()
            
            # Log token usage
            if hasattr(response, 'usage'):
                usage = response.usage
                logger.debug(f"Token usage - prompt: {usage.prompt_tokens}, "
                           f"completion: {usage.completion_tokens}, total: {usage.total_tokens}")
            
            # Validate category
            if category not in self.valid_categories:
                logger.warning(f"Invalid category '{category}' returned, using default '{self.default_category}'")
                return self.default_category
            
            logger.debug(f"Classification result: {category}")
            return category
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return self.default_category
    
    def _create_classification_prompt(self, subject: str, body: str) -> str:
        """Create a well-structured prompt for email classification."""
        return f"""You are an email classification system for customer support. 
Classify the email below into exactly one of these categories:

Categories:
- order: Questions about existing orders, order status, shipping, delivery, returns, refunds
- inquiry: Product questions, general information requests, technical support
- other: All other emails including greetings, complaints, feedback, spam

Email to classify:
Subject: {subject}

Body:
{body}

Instructions:
- Respond with ONLY the category name in lowercase
- Do not include any explanation or additional text
- Valid responses are: order, inquiry, other

Category:"""
    
    def classify_dataframe(self, df: pd.DataFrame, subject_col: str = 'subject', body_col: str = 'body') -> pd.DataFrame:
        """
        Classify emails in a pandas DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame containing emails
            subject_col (str): Name of subject column
            body_col (str): Name of body column
            
        Returns:
            pd.DataFrame: DataFrame with added 'category' column
        """
        logger.info(f"Starting classification of {len(df)} emails...")
        
        # Validate required columns
        if subject_col not in df.columns:
            raise ValueError(f"Subject column '{subject_col}' not found in DataFrame")
        if body_col not in df.columns:
            raise ValueError(f"Body column '{body_col}' not found in DataFrame")
        
        # Process emails
        categories = []
        start_time = time.time()
        
        for idx, row in df.iterrows():
            try:
                subject = row[subject_col]
                body = row[body_col]
                category = self.classify_single_email(subject, body)
                categories.append(category)
                
                # Progress logging
                if (idx + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (idx + 1)
                    remaining = (len(df) - idx - 1) * avg_time
                    logger.info(f"Progress: {idx + 1}/{len(df)} ({(idx+1)/len(df)*100:.1f}%) - "
                               f"ETA: {remaining:.1f}s")
                
            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                categories.append(self.default_category)
        
        # Add results to DataFrame
        df = df.copy()
        df['category'] = categories
        
        # Log results summary
        total_time = time.time() - start_time
        logger.info(f"Classification completed in {total_time:.2f} seconds")
        
        # Category distribution
        category_counts = df['category'].value_counts()
        logger.info("Classification results:")
        for category, count in category_counts.items():
            percentage = count / len(df) * 100
            logger.info(f"  {category}: {count} emails ({percentage:.1f}%)")
        
        return df
    
    def run_tests(self) -> bool:
        """Run test cases to validate classification functionality."""
        logger.info("Running email classification tests...")
        
        test_cases = [
            {
                "subject": "Where is my order?",
                "body": "Hi, I haven't received my order yet. Can you help?",
                "expected": "order",
                "description": "Order status inquiry"
            },
            {
                "subject": "Product Inquiry",
                "body": "Do you have this product available in red color?",
                "expected": "inquiry",
                "description": "Product availability question"
            },
            {
                "subject": "Return request",
                "body": "I would like to return item #12345 as it doesn't fit",
                "expected": "order",
                "description": "Return request"
            },
            {
                "subject": "Hi there",
                "body": "Just saying hello and thanks for your service!",
                "expected": "other",
                "description": "General greeting"
            }
        ]
        
        passed = 0
        for i, test in enumerate(test_cases, 1):
            try:
                result = self.classify_single_email(test["subject"], test["body"])
                if result == test["expected"]:
                    logger.info(f"✅ Test {i} PASSED: {test['description']} -> {result}")
                    passed += 1
                else:
                    logger.warning(f"❌ Test {i} FAILED: {test['description']} -> "
                                 f"expected {test['expected']}, got {result}")
            except Exception as e:
                logger.error(f"❌ Test {i} ERROR: {e}")
        
        success_rate = passed / len(test_cases) * 100
        logger.info(f"Test results: {passed}/{len(test_cases)} passed ({success_rate:.1f}%)")
        return passed == len(test_cases)


def create_sample_data() -> pd.DataFrame:
    """Create sample email data for testing."""
    sample_emails = [
        {
            "email_id": "E001",
            "subject": "Where is my order #12345?",
            "body": "Hi, I placed order #12345 last week and haven't received it yet. Can you please check the status?"
        },
        {
            "email_id": "E002", 
            "subject": "Product question about laptop",
            "body": "Do you have the XYZ laptop model available in 16GB RAM configuration? What's the price?"
        },
        {
            "email_id": "E003",
            "subject": "Return request",
            "body": "I received the wrong item in my order. I ordered a blue shirt but got a red one. Please help with return."
        },
        {
            "email_id": "E004",
            "subject": "Thank you!",
            "body": "Just wanted to say thanks for the excellent customer service. Keep up the good work!"
        }
    ]
    
    return pd.DataFrame(sample_emails)


def main():
    """Main function demonstrating the email classification system."""
    try:
        logger.info("=" * 60)
        logger.info("Email Classification System Demo")
        logger.info("=" * 60)
        
        # Configuration
        api_key = 'a0BIj000002vVUoMAM'
        base_url = 'https://47v4us7kyypinfb5lcligtc3x40ygqbs.lambda-url.us-east-1.on.aws/v1/'
        model = "gpt-4o"
        
        # Initialize classifier
        classifier = EmailClassifier(api_key=api_key, base_url=base_url, model=model)
        
        # Run tests
        logger.info("Step 1: Running validation tests...")
        test_success = classifier.run_tests()
        
        # Create and process sample data
        logger.info("Step 2: Processing sample email data...")
        sample_df = create_sample_data()
        
        logger.info("Sample data:")
        for _, row in sample_df.iterrows():
            logger.info(f"  ID: {row['email_id']}, Subject: '{row['subject']}'")
        
        # Classify emails
        logger.info("Step 3: Classifying emails...")
        results_df = classifier.classify_dataframe(sample_df, 'subject', 'body')
        
        # Display results
        logger.info("Step 4: Classification results:")
        for _, row in results_df.iterrows():
            logger.info(f"  ID: {row['email_id']}, Category: {row['category']}, "
                       f"Subject: '{row['subject'][:40]}...'")
        
        # Save results
        output_file = "email_classification_results.csv"
        results_df.to_csv(output_file, index=False)
        logger.info(f"Results saved to: {output_file}")
        
        logger.info("=" * 60)
        logger.info("Email classification completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise


if __name__ == "__main__":
    main()
