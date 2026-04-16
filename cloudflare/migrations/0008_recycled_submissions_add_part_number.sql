-- Migration: Add matched_part_number to recycled_device_submissions
ALTER TABLE recycled_device_submissions ADD COLUMN matched_part_number TEXT;
