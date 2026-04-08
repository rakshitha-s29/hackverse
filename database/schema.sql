-- VoyageVeda: SingleStore Vector Memory Schema

-- 1. Create the Database if not exists
-- CREATE DATABASE IF NOT EXISTS voyage_veda;
-- USE voyage_veda;

-- 2. Long Term Memory (Vector table for RAG)
CREATE TABLE IF NOT EXISTS user_memories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id TEXT NOT NULL,
    memory_type TEXT NOT NULL, -- 'preference', 'past_trip', 'fact'
    content TEXT NOT NULL,
    metadata JSON,
    -- vector_content VECTOR(1536), -- For future embeddings integration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Saved Itineraries
CREATE TABLE IF NOT EXISTS itineraries (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username TEXT NOT NULL,
    destination TEXT NOT NULL,
    source_location TEXT,
    days INT,
    itinerary_json JSON,
    markup_content LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Agent Task Logs (For observability)
CREATE TABLE IF NOT EXISTS agent_task_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id TEXT NOT NULL,
    task_name TEXT,
    status TEXT, -- 'thinking', 'acting', 'evaluating'
    thinking_process TEXT,
    tool_calls TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
