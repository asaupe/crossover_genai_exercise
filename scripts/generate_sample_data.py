#!/usr/bin/env python3
"""
Sample data generator for testing the GenAI Email Processing System.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.data.models import EmailRequest


class SampleDataGenerator:
    """Generate sample emails for testing."""
    
    def __init__(self):
        self.sample_subjects = [
            "Order Issue - Need Help",
            "Can't Access My Account",
            "Billing Question",
            "Product Defect Report",
            "Request for Refund",
            "Technical Support Needed",
            "Shipping Delay Inquiry",
            "Password Reset Problems",
            "Feature Request",
            "General Inquiry",
            "Urgent: System Down",
            "Thank You for Great Service",
            "Complaint About Service",
            "Order Confirmation",
            "Invoice Discrepancy"
        ]
        
        self.sample_bodies = [
            "I'm having trouble with my recent order #12345. The item I received doesn't match what I ordered.",
            "I can't log into my account. Every time I try, it says my credentials are invalid.",
            "I have a question about my latest bill. There's a charge I don't recognize.",
            "The product I received is defective. It stopped working after just one day.",
            "I'd like to return this item and get a full refund. It doesn't meet my expectations.",
            "I need technical support with setting up the software. The installation keeps failing.",
            "My order was supposed to arrive yesterday but it hasn't shown up yet.",
            "I'm trying to reset my password but I'm not receiving the reset email.",
            "Could you add a dark mode feature to your application? It would be very helpful.",
            "I have some general questions about your services and pricing plans.",
            "Our production system is completely down. This is affecting our entire business operation.",
            "I wanted to thank you for the excellent customer service. The support team was very helpful.",
            "I'm extremely disappointed with the quality of service. This is unacceptable.",
            "Please confirm that my order #67890 has been processed and shipped.",
            "There's an error on my invoice. The amount charged doesn't match the quoted price."
        ]
        
        self.sample_senders = [
            "john.doe@email.com",
            "sarah.smith@company.com",
            "mike.johnson@business.org",
            "emma.wilson@startup.io",
            "david.brown@enterprise.net",
            "lisa.davis@customer.com",
            "alex.taylor@user.org",
            "jennifer.clark@client.co",
            "robert.martinez@buyer.com",
            "amanda.lee@subscriber.net"
        ]
    
    def generate_email(self) -> EmailRequest:
        """Generate a single sample email."""
        subject = random.choice(self.sample_subjects)
        body = random.choice(self.sample_bodies)
        sender = random.choice(self.sample_senders)
        
        # Add some variation
        if random.random() < 0.3:  # 30% chance of urgent keywords
            urgent_words = ["urgent", "critical", "emergency", "asap", "immediately"]
            subject = f"{random.choice(urgent_words).upper()}: {subject}"
        
        if random.random() < 0.2:  # 20% chance of attachments
            attachments = [f"attachment_{i}.pdf" for i in range(random.randint(1, 3))]
        else:
            attachments = []
        
        metadata = {
            "source": "web_form",
            "user_agent": "Mozilla/5.0...",
            "ip_address": f"192.168.1.{random.randint(1, 254)}",
            "timestamp": datetime.now().isoformat()
        }
        
        return EmailRequest(
            subject=subject,
            body=body,
            sender=sender,
            attachments=attachments,
            metadata=metadata
        )
    
    def generate_batch(self, count: int) -> List[EmailRequest]:
        """Generate a batch of sample emails."""
        return [self.generate_email() for _ in range(count)]
    
    def save_to_file(self, emails: List[EmailRequest], filename: str):
        """Save emails to JSON file."""
        email_data = []
        for email in emails:
            email_data.append({
                "subject": email.subject,
                "body": email.body,
                "sender": email.sender,
                "attachments": email.attachments,
                "metadata": email.metadata
            })
        
        with open(filename, 'w') as f:
            json.dump(email_data, f, indent=2)
        
        print(f"Saved {len(emails)} sample emails to {filename}")


async def main():
    """Generate and save sample data."""
    generator = SampleDataGenerator()
    
    # Generate different batches for testing
    test_emails = generator.generate_batch(50)
    generator.save_to_file(test_emails, "sample_emails.json")
    
    # Generate a smaller batch for quick testing
    quick_test_emails = generator.generate_batch(10)
    generator.save_to_file(quick_test_emails, "quick_test_emails.json")
    
    print("Sample data generation complete!")
    print("Files created:")
    print("- sample_emails.json (50 emails)")
    print("- quick_test_emails.json (10 emails)")


if __name__ == "__main__":
    asyncio.run(main())
