#!/usr/bin/env python3
"""
Email Classification System for Customer Support

This module implements an AI-powered email classification system that categorizes
customer support emails into predefined categories using OpenAI's GPT model.
The system processes emails from Google Sheets and returns classified results.

Author: Assessment Developer
Date: June 2025
Purpose: Crossover GenAI Assessment - Email Classification Component
"""

import logging
import sys
import time
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

import pandas as pd
from openai import OpenAI
from gspread_dataframe import set_with_dataframe

# Configure comprehensive logging
def setup_logging() -> logging.Logger:
    """
    Set up comprehensive logging configuration for the email classification system.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter for consistent log format
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set up root logger
    logger = logging.getLogger("email_classifier")
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler for immediate feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_dir / "email_classification.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler for errors only
    error_handler = logging.FileHandler(log_dir / "email_classification_errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    logger.info("Logging system initialized successfully")
    return logger


# Initialize logger
logger = setup_logging()

# Configuration constants
class Config:
    """Configuration settings for the email classification system."""
    
    # OpenAI API Configuration
    OPENAI_BASE_URL = 'https://47v4us7kyypinfb5lcligtc3x40ygqbs.lambda-url.us-east-1.on.aws/v1/'
    OPENAI_API_KEY = 'a0BIj000002vVUoMAM'
    OPENAI_MODEL = "gpt-4o"
    
    # Google Sheets Configuration
    DOCUMENT_ID = '14fKHsblfqZfWj3iAaM2oA51TlYfQlFT4WKo52fVaQ9U'
    INPUT_SHEET_NAME = 'emails'
    OUTPUT_SHEET_NAME = 'email-classification'
    OUTPUT_DOCUMENT_NAME = 'Solving Business Problems with AI - Output'
    
    # Classification Settings
    VALID_CATEGORIES = ["order", "inquiry", "other"]
    DEFAULT_CATEGORY = "other"
    
    # Processing Settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds
    BATCH_SIZE = 10    # for progress reporting


def initialize_openai_client() -> OpenAI:
    """
    Initialize and configure the OpenAI client with proper error handling.
    
    Returns:
        OpenAI: Configured OpenAI client instance
        
    Raises:
        Exception: If client initialization fails
    """
    try:
        logger.info("Initializing OpenAI client...")
        logger.debug(f"Using base URL: {Config.OPENAI_BASE_URL}")
        logger.debug(f"Using model: {Config.OPENAI_MODEL}")
        
        client = OpenAI(
            base_url=Config.OPENAI_BASE_URL,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Test the client with a simple request
        logger.debug("Testing OpenAI client connection...")
        test_response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5
        )
        
        logger.info("OpenAI client initialized and tested successfully")
        return client
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        logger.error(f"Check your API configuration and network connection")
        raise


def read_data_frame(document_id: str, sheet_name: str) -> pd.DataFrame:
    """
    Read data from Google Sheets and return as pandas DataFrame.
    
    Args:
        document_id (str): Google Sheets document ID
        sheet_name (str): Name of the sheet to read from
        
    Returns:
        pd.DataFrame: DataFrame containing the sheet data
        
    Raises:
        Exception: If data reading fails
    """
    try:
        logger.info(f"Reading data from Google Sheets...")
        logger.debug(f"Document ID: {document_id}")
        logger.debug(f"Sheet name: {sheet_name}")
        
        # Construct the export URL for CSV format
        export_link = f"https://docs.google.com/spreadsheets/d/{document_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        logger.debug(f"Export URL: {export_link}")
        
        # Read the CSV data
        df = pd.read_csv(export_link)
        
        # Log data summary
        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
        logger.debug(f"Columns: {list(df.columns)}")
        logger.debug(f"Data types: {dict(df.dtypes)}")
        
        # Validate required columns
        required_columns = ['subject', 'body']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for empty data
        if df.empty:
            logger.warning("Loaded DataFrame is empty")
        else:
            # Log sample of the data (first few rows, truncated)
            logger.debug("Sample data (first 3 rows):")
            for idx, row in df.head(3).iterrows():
                logger.debug(f"  Row {idx}: subject='{str(row.get('subject', 'N/A'))[:50]}...', "
                           f"body='{str(row.get('body', 'N/A'))[:50]}...'")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to read data from Google Sheets: {str(e)}")
        logger.error(f"Check document ID, sheet name, and permissions")
        raise


def classify_email(client: OpenAI, subject: str, body: str, retry_count: int = 0) -> str:
    """
    Classify a single email into predefined categories using OpenAI GPT.
    
    Args:
        client (OpenAI): Configured OpenAI client
        subject (str): Email subject line
        body (str): Email body content
        retry_count (int): Current retry attempt (for internal use)
        
    Returns:
        str: Classification category ('order', 'inquiry', or 'other')
    """
    # Input validation and sanitization
    if not isinstance(subject, str):
        subject = str(subject) if subject is not None else ""
    if not isinstance(body, str):
        body = str(body) if body is not None else ""
    
    # Truncate inputs if too long to avoid token limits
    max_subject_length = 200
    max_body_length = 2000
    
    if len(subject) > max_subject_length:
        subject = subject[:max_subject_length] + "..."
        logger.debug(f"Truncated subject to {max_subject_length} characters")
    
    if len(body) > max_body_length:
        body = body[:max_body_length] + "..."
        logger.debug(f"Truncated body to {max_body_length} characters")
    
    # Construct the classification prompt
    prompt = (
        f"You are an email classification system for customer support. "
        f"Classify the email below into exactly one of these categories:\n\n"
        f"Categories:\n"
        f"- order: Questions about existing orders, order status, shipping, delivery, returns, refunds\n"
        f"- inquiry: Product questions, general information requests, technical support\n"
        f"- other: All other emails including greetings, complaints, feedback, spam\n\n"
        f"Email to classify:\n"
        f"Subject: {subject}\n\n"
        f"Body:\n{body}\n\n"
        f"Instructions:\n"
        f"- Respond with ONLY the category name in lowercase\n"
        f"- Do not include any explanation or additional text\n"
        f"- Valid responses are: order, inquiry, other\n\n"
        f"Category:"
    )
    
    try:
        logger.debug(f"Classifying email with subject: '{subject[:50]}...'")
        
        # Make API request to OpenAI
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,  # We only need a single word response
            temperature=0.1,  # Low temperature for consistent classification
            top_p=1.0
        )
        
        # Extract and validate the response
        category = response.choices[0].message.content.strip().lower()
        
        # Log token usage for monitoring
        if hasattr(response, 'usage'):
            logger.debug(f"Token usage - prompt: {response.usage.prompt_tokens}, "
                        f"completion: {response.usage.completion_tokens}, "
                        f"total: {response.usage.total_tokens}")
        
        # Validate the category
        if category not in Config.VALID_CATEGORIES:
            logger.warning(f"Invalid category '{category}' returned by AI - defaulting to '{Config.DEFAULT_CATEGORY}'")
            logger.debug(f"Full AI response was: '{response.choices[0].message.content}'")
            return Config.DEFAULT_CATEGORY
        
        logger.debug(f"Successfully classified email as: '{category}'")
        return category
        
    except Exception as e:
        logger.error(f"Error classifying email (attempt {retry_count + 1}): {str(e)}")
        
        # Implement retry logic
        if retry_count < Config.MAX_RETRIES - 1:
            logger.info(f"Retrying classification in {Config.RETRY_DELAY} seconds...")
            time.sleep(Config.RETRY_DELAY)
            return classify_email(client, subject, body, retry_count + 1)
        else:
            logger.error(f"Failed to classify email after {Config.MAX_RETRIES} attempts - defaulting to '{Config.DEFAULT_CATEGORY}'")
            logger.debug(f"Failed email subject: '{subject[:100]}'")
            return Config.DEFAULT_CATEGORY


def process_email_batch(client: OpenAI, emails_df: pd.DataFrame) -> pd.DataFrame:
    """
    Process a batch of emails for classification with progress tracking.
    
    Args:
        client (OpenAI): Configured OpenAI client
        emails_df (pd.DataFrame): DataFrame containing emails to classify
        
    Returns:
        pd.DataFrame: DataFrame with added 'category' column
    """
    logger.info(f"Starting batch processing of {len(emails_df)} emails...")
    
    # Initialize results list
    categories = []
    processed_count = 0
    error_count = 0
    
    # Track processing time
    start_time = time.time()
    
    # Process each email
    for idx, row in emails_df.iterrows():
        try:
            # Extract email data
            subject = row.get('subject', '')
            body = row.get('body', '')
            
            # Classify the email
            category = classify_email(client, subject, body)
            categories.append(category)
            
            processed_count += 1
            
            # Log progress every batch_size emails
            if processed_count % Config.BATCH_SIZE == 0:
                elapsed_time = time.time() - start_time
                avg_time_per_email = elapsed_time / processed_count
                remaining_emails = len(emails_df) - processed_count
                estimated_remaining_time = remaining_emails * avg_time_per_email
                
                logger.info(f"Progress: {processed_count}/{len(emails_df)} emails processed "
                           f"({processed_count/len(emails_df)*100:.1f}%) - "
                           f"ETA: {estimated_remaining_time:.1f}s")
            
        except Exception as e:
            logger.error(f"Error processing email at index {idx}: {str(e)}")
            categories.append(Config.DEFAULT_CATEGORY)
            error_count += 1
    
    # Add categories to DataFrame
    emails_df['category'] = categories
    
    # Log final statistics
    total_time = time.time() - start_time
    avg_time_per_email = total_time / len(emails_df)
    
    logger.info(f"Batch processing completed in {total_time:.2f} seconds")
    logger.info(f"Average time per email: {avg_time_per_email:.2f} seconds")
    logger.info(f"Successfully processed: {processed_count - error_count} emails")
    if error_count > 0:
        logger.warning(f"Errors encountered: {error_count} emails")
    
    # Log category distribution
    category_counts = emails_df['category'].value_counts()
    logger.info("Classification results:")
    for category, count in category_counts.items():
        percentage = count / len(emails_df) * 100
        logger.info(f"  {category}: {count} emails ({percentage:.1f}%)")
    
    return emails_df


def write_results_to_sheet(emails_df: pd.DataFrame) -> bool:
    """
    Write classification results to Google Sheets.
    
    Args:
        emails_df (pd.DataFrame): DataFrame with classification results
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("Attempting to write results to Google Sheets...")
        
        # Import required libraries
        import gspread
        from google.auth import default
        
        # Authenticate with Google Sheets
        logger.debug("Authenticating with Google Sheets...")
        creds, _ = default()
        gc = gspread.authorize(creds)
        
        # Open the output spreadsheet
        logger.debug(f"Opening spreadsheet: '{Config.OUTPUT_DOCUMENT_NAME}'")
        output_document = gc.open(Config.OUTPUT_DOCUMENT_NAME)
        
        # Select the output worksheet
        logger.debug(f"Selecting worksheet: '{Config.OUTPUT_SHEET_NAME}'")
        sheet = output_document.worksheet(Config.OUTPUT_SHEET_NAME)
        
        # Prepare data for writing (only ID and category columns)
        output_columns = ['email ID', 'category'] if 'email ID' in emails_df.columns else ['category']
        output_data = emails_df[output_columns]
        
        logger.debug(f"Writing {len(output_data)} rows to sheet starting at row 2")
        
        # Write data to sheet (starting at row 2 to preserve headers)
        set_with_dataframe(sheet, output_data, row=2, include_column_header=False)
        
        logger.info(f"Successfully wrote {len(output_data)} results to Google Sheets")
        return True
        
    except ImportError as e:
        logger.warning(f"Google Sheets libraries not available: {e}")
        logger.info("Install with: pip install gspread google-auth")
        return False
        
    except Exception as e:
        logger.error(f"Failed to write results to Google Sheets: {str(e)}")
        logger.error("Check your Google authentication and sheet permissions")
        return False


def run_test_cases(client: OpenAI) -> bool:
    """
    Run test cases to validate the email classification functionality.
    
    Args:
        client (OpenAI): Configured OpenAI client
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    logger.info("Running email classification test cases...")
    
    # Define test cases with expected outcomes
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
        },
        {
            "subject": "Technical support needed",
            "body": "How do I install this software on my computer?",
            "expected": "inquiry",
            "description": "Technical support question"
        }
    ]
    
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            logger.debug(f"Running test case {i}/{total_tests}: {test_case['description']}")
            
            # Classify the test email
            result = classify_email(client, test_case["subject"], test_case["body"])
            
            # Check if result matches expected category
            if result == test_case["expected"]:
                logger.info(f"✅ Test {i} PASSED: '{test_case['description']}' -> '{result}'")
                passed_tests += 1
            else:
                logger.warning(f"❌ Test {i} FAILED: '{test_case['description']}' -> "
                             f"expected '{test_case['expected']}', got '{result}'")
                
        except Exception as e:
            logger.error(f"❌ Test {i} ERROR: {str(e)}")
    
    # Log test summary
    success_rate = passed_tests / total_tests * 100
    logger.info(f"Test results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        logger.info("🎉 All test cases passed!")
        return True
    else:
        logger.warning(f"⚠️ {total_tests - passed_tests} test(s) failed")
        return False


def main():
    """
    Main function to orchestrate the email classification process.
    """
    try:
        logger.info("=" * 60)
        logger.info("Email Classification System Starting")
        logger.info("=" * 60)
        
        # Step 1: Initialize OpenAI client
        logger.info("Step 1: Initializing OpenAI client...")
        client = initialize_openai_client()
        
        # Step 2: Load email data
        logger.info("Step 2: Loading email data from Google Sheets...")
        emails_df = read_data_frame(Config.DOCUMENT_ID, Config.INPUT_SHEET_NAME)
        
        # Step 3: Run test cases to validate system
        logger.info("Step 3: Running validation tests...")
        test_success = run_test_cases(client)
        if not test_success:
            logger.warning("Some tests failed, but continuing with processing...")
        
        # Step 4: Process emails for classification
        logger.info("Step 4: Processing emails for classification...")
        emails_df = process_email_batch(client, emails_df)
        
        # Step 5: Display sample results
        logger.info("Step 5: Displaying sample results...")
        if 'email ID' in emails_df.columns:
            sample_columns = ['email ID', 'subject', 'category']
        else:
            sample_columns = ['subject', 'category']
        
        sample_data = emails_df[sample_columns].head(5)
        logger.info("Sample classification results:")
        for idx, row in sample_data.iterrows():
            if 'email ID' in sample_columns:
                logger.info(f"  ID: {row['email ID']}, Subject: '{row['subject'][:40]}...', Category: {row['category']}")
            else:
                logger.info(f"  Subject: '{row['subject'][:40]}...', Category: {row['category']}")
        
        # Step 6: Write results to Google Sheets (optional)
        logger.info("Step 6: Writing results to Google Sheets...")
        write_success = write_results_to_sheet(emails_df)
        
        # Step 7: Save results locally as backup
        logger.info("Step 7: Saving results locally...")
        output_file = "email_classification_results.csv"
        emails_df.to_csv(output_file, index=False)
        logger.info(f"Results saved to: {output_file}")
        
        # Final summary
        logger.info("=" * 60)
        logger.info("Email Classification System Completed Successfully")
        logger.info(f"Processed: {len(emails_df)} emails")
        logger.info(f"Google Sheets write: {'Success' if write_success else 'Failed'}")
        logger.info(f"Local backup: {output_file}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}")
        logger.error("Email classification system failed to complete")
        raise


if __name__ == "__main__":
    """
    Entry point for the email classification system.
    """
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        sys.exit(1)
