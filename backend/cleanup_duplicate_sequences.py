"""
One-time cleanup script to remove duplicate email sequences.

This script identifies and removes duplicate email sequences for the same order,
keeping only the earliest sequence created.

Run with: python cleanup_duplicate_sequences.py
"""

from app import app
from database import db, EmailSequence
from collections import defaultdict

def cleanup_duplicates():
    """Remove duplicate email sequences, keeping the earliest one per order."""

    with app.app_context():
        print("=== Email Sequence Duplicate Cleanup ===\n")

        # Get all email sequences
        all_sequences = EmailSequence.query.order_by(EmailSequence.order_id, EmailSequence.id).all()

        # Group by order_id
        sequences_by_order = defaultdict(list)
        for seq in all_sequences:
            sequences_by_order[seq.order_id].append(seq)

        # Find duplicates
        total_deleted = 0

        for order_id, sequences in sequences_by_order.items():
            # Group by day_number within the order
            by_day = defaultdict(list)
            for seq in sequences:
                by_day[seq.day_number].append(seq)

            # Check if there are duplicates
            has_duplicates = any(len(day_seqs) > 1 for day_seqs in by_day.values())

            if has_duplicates:
                print(f"\n📦 Order {order_id}:")
                print(f"   Customer ID: {sequences[0].customer_id}")
                print(f"   Total sequences: {len(sequences)}")

                # Count duplicates by day
                duplicate_days = [day for day, seqs in by_day.items() if len(seqs) > 1]
                print(f"   Duplicate days: {len(duplicate_days)}")

                # For each day, keep the earliest (lowest ID), delete the rest
                for day_number, day_seqs in by_day.items():
                    if len(day_seqs) > 1:
                        # Sort by ID (earliest first)
                        day_seqs.sort(key=lambda s: s.id)

                        # Keep the first, delete the rest
                        to_keep = day_seqs[0]
                        to_delete = day_seqs[1:]

                        for seq in to_delete:
                            print(f"   ❌ Deleting duplicate Day {day_number} (ID: {seq.id}, Status: {seq.status})")
                            db.session.delete(seq)
                            total_deleted += 1

        if total_deleted > 0:
            # Commit the changes
            print(f"\n💾 Committing changes...")
            db.session.commit()
            print(f"✅ Successfully deleted {total_deleted} duplicate sequences")
        else:
            print("\n✅ No duplicates found!")

        # Summary
        print("\n=== Summary ===")
        remaining = EmailSequence.query.count()
        print(f"Remaining email sequences: {remaining}")
        print(f"Deleted duplicates: {total_deleted}")

        # Show orders with sequences
        orders_with_sequences = db.session.query(EmailSequence.order_id).distinct().count()
        print(f"Orders with email sequences: {orders_with_sequences}")


if __name__ == '__main__':
    try:
        cleanup_duplicates()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
