-- Create threads table
CREATE TABLE threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT,
  openai_thread_id TEXT,
  vector_store_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE threads ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own threads
CREATE POLICY "Users can CRUD own threads" ON threads
  FOR ALL USING (auth.uid() = user_id);

-- Create index for user_id lookups
CREATE INDEX idx_threads_user_id ON threads(user_id);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_threads_updated_at
  BEFORE UPDATE ON threads
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
