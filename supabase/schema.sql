-- Lesson Lab 2.0 Database Schema
-- This file creates the database tables and policies for the lesson planning app

-- Create lesson_plans table
CREATE TABLE lesson_plans (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE,
  title TEXT,
  topic TEXT NOT NULL,
  grade TEXT NOT NULL,
  duration INTEGER DEFAULT 60, -- minutes
  plan_json JSONB NOT NULL,
  agent_thoughts JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX idx_lesson_plans_user_id ON lesson_plans(user_id);
CREATE INDEX idx_lesson_plans_created_at ON lesson_plans(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE lesson_plans ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own lesson plans
CREATE POLICY "Users can view own lesson plans" ON lesson_plans
  FOR SELECT USING (auth.uid() = user_id);

-- Users can insert their own lesson plans
CREATE POLICY "Users can insert own lesson plans" ON lesson_plans
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own lesson plans
CREATE POLICY "Users can update own lesson plans" ON lesson_plans
  FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own lesson plans
CREATE POLICY "Users can delete own lesson plans" ON lesson_plans
  FOR DELETE USING (auth.uid() = user_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_lesson_plans_updated_at 
  BEFORE UPDATE ON lesson_plans
  FOR EACH ROW 
  EXECUTE FUNCTION update_updated_at_column();