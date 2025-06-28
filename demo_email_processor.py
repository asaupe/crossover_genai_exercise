#!/usr/bin/env python3
"""
Demo script for the GenAI Email Processing System

This script demonstrates both implementations:
1. Simple email classification
2. Enhanced email processing with Google Sheets integration

Usage:
    python demo_email_processor.py
"""

import os
import sys
import pandas as pd
from typing import Dict, Any, List
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from simple_email_classifier import EmailClassifier, create_sample_data
    from enhanced_email_classifier import initialize_openai_client, classify_email
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


def demo_simple_classifier():
    """Demonstrate the simple email classifier."""
    print("🔍 Simple Email Classifier Demo")
    print("=" * 50)
    
    # Configuration
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        return False
    
    try:
        # Initialize classifier
        classifier = EmailClassifier(api_key=api_key, model="gpt-4o")
        
        # Create sample data
        print("📧 Creating sample email data...")
        sample_df = create_sample_data()
        
        print(f"📊 Processing {len(sample_df)} sample emails...")
        
        # Classify emails
        results_df = classifier.classify_dataframe(sample_df, 'subject', 'body')
        
        # Display results
        print("\n🎯 Classification Results:")
        print("-" * 60)
        for _, row in results_df.iterrows():
            print(f"ID: {row['email_id']}")
            print(f"Subject: {row['subject']}")
            print(f"Category: {row['category']}")
            print("-" * 60)
        
        # Save results
        output_file = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(output_file, index=False)
        print(f"✅ Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in simple classifier demo: {e}")
        return False


def demo_enhanced_processing():
    """Demonstrate enhanced email processing capabilities."""
    print("\n🚀 Enhanced Email Processing Demo")
    print("=" * 50)
    
    try:
        # Initialize OpenAI client
        client = initialize_openai_client()
        
        # Sample emails for enhanced processing
        sample_emails = [
            {
                "subject": "Order inquiry for blue jeans",
                "body": "Hi, I want to order 2 pairs of blue jeans in size medium. Do you have them in stock?",
                "expected": "order"
            },
            {
                "subject": "Product information request",
                "body": "Can you tell me more about your summer collection? What materials do you use?",
                "expected": "inquiry"
            },
            {
                "subject": "Shipping update needed",
                "body": "I placed order #12345 last week. Can you provide a shipping update?",
                "expected": "order"
            },
            {
                "subject": "Return policy question",
                "body": "What is your return policy for items that don't fit properly?",
                "expected": "inquiry"
            }
        ]
        
        print(f"📧 Processing {len(sample_emails)} enhanced test emails...")
        
        results = []
        for i, email in enumerate(sample_emails, 1):
            print(f"\n📧 Email {i}:")
            print(f"Subject: {email['subject']}")
            print(f"Expected: {email['expected']}")
            
            # Classify using enhanced method
            category = classify_email(client, email['subject'], email['body'])
            
            result = {
                "email_id": f"DEMO_{i:03d}",
                "subject": email['subject'],
                "body": email['body'],
                "expected_category": email['expected'],
                "predicted_category": category,
                "correct": category == email['expected']
            }
            
            results.append(result)
            
            print(f"Predicted: {category}")
            print(f"Correct: {'✅' if result['correct'] else '❌'}")
        
        # Calculate accuracy
        correct_predictions = sum(1 for r in results if r['correct'])
        accuracy = correct_predictions / len(results) * 100
        
        print(f"\n📊 Demo Results Summary:")
        print(f"Total emails: {len(results)}")
        print(f"Correct predictions: {correct_predictions}")
        print(f"Accuracy: {accuracy:.1f}%")
        
        # Save enhanced results
        results_df = pd.DataFrame(results)
        output_file = f"enhanced_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(output_file, index=False)
        print(f"✅ Enhanced results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced processing demo: {e}")
        return False


def demo_jupyter_notebook_info():
    """Provide information about the Jupyter notebook demo."""
    print("\n📓 Jupyter Notebook Demo")
    print("=" * 50)
    
    print("🎯 For the complete interactive experience, use the Jupyter notebook:")
    print("   📁 File: fashion_store_email_processor.ipynb")
    print("   ☁️  Google Colab: Upload to colab.research.google.com")
    print("   🔑 Set OPENAI_API_KEY in Colab Secrets")
    print("   ▶️  Runtime → Run all")
    print()
    print("📊 The notebook includes:")
    print("   • Complete AI pipeline with RAG implementation")
    print("   • Google Sheets data loading")
    print("   • ChromaDB vector store for semantic search")
    print("   • Advanced order processing with inventory management")
    print("   • Professional response generation")
    print("   • Multi-sheet Excel export")
    print()
    print("📈 Expected outputs:")
    print("   • email-classification: Categories and confidence scores")
    print("   • order-status: Processing results and inventory updates")
    print("   • order-response: AI-generated professional responses")
    print("   • inquiry-response: RAG-enhanced product information")


def main():
    """Main demo function."""
    print("🎉 GenAI Email Processing System - Demo")
    print("=" * 60)
    print("This demo showcases the email classification capabilities")
    print("of our AI-powered system using OpenAI GPT models.")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found!")
        print("Please set your API key:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   or add it to your .env file")
        sys.exit(1)
    
    print(f"✅ OpenAI API key found (length: {len(api_key)})")
    
    # Run demos
    success_count = 0
    
    # Demo 1: Simple classifier
    if demo_simple_classifier():
        success_count += 1
    
    # Demo 2: Enhanced processing
    if demo_enhanced_processing():
        success_count += 1
    
    # Demo 3: Jupyter notebook info
    demo_jupyter_notebook_info()
    
    # Final summary
    print(f"\n🎯 Demo Summary:")
    print(f"Completed {success_count}/2 demo sections successfully")
    print(f"📁 Check the generated CSV files for detailed results")
    
    if success_count == 2:
        print("🎉 All demos completed successfully!")
        print("🚀 Ready for production deployment!")
    else:
        print("⚠️  Some demos had issues. Check the error messages above.")
    
    print("\n📚 Next Steps:")
    print("1. 📓 Try the Jupyter notebook for interactive analysis")
    print("2. 🚀 Deploy the FastAPI service for production use")
    print("3. 📖 Review the documentation in README.md")
    print("4. 🎯 Customize for your specific use case")


if __name__ == "__main__":
    main()
