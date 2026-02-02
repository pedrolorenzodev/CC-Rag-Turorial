-- Create messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view messages in their own threads
CREATE POLICY "Users can view own messages" ON messages
  FOR SELECT USING (EXISTS (
    SELECT 1 FROM threads WHERE threads.id = messages.thread_id AND threads.user_id = auth.uid()
  ));

-- Policy: Users can insert messages to their own threads
CREATE POLICY "Users can insert own messages" ON messages
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create indexes for performance
CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
