-- Intelligence OS Database Initialization Script
-- Oracle 9.1 Protocol Compliant Database Schema

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS oracle_protocol;
CREATE SCHEMA IF NOT EXISTS ai_processing;
CREATE SCHEMA IF NOT EXISTS voice_processing;
CREATE SCHEMA IF NOT EXISTS integrations;

-- Set search path
SET search_path TO public, oracle_protocol, ai_processing, voice_processing, integrations;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    preferences JSONB DEFAULT '{}'::jsonb
);

-- Organizations table
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Meetings table (Oracle 9.1 Protocol compliant)
CREATE TABLE IF NOT EXISTS oracle_protocol.meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration INTEGER, -- in minutes
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'scheduled',
    context TEXT,
    agenda JSONB DEFAULT '[]'::jsonb,
    participants JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation transcripts
CREATE TABLE IF NOT EXISTS oracle_protocol.conversation_transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    segments JSONB NOT NULL DEFAULT '[]'::jsonb,
    speakers JSONB NOT NULL DEFAULT '{}'::jsonb,
    timeline JSONB NOT NULL DEFAULT '[]'::jsonb,
    topics JSONB NOT NULL DEFAULT '[]'::jsonb,
    raw_transcript TEXT,
    processed_transcript TEXT,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Six-dimensional analysis results
CREATE TABLE IF NOT EXISTS oracle_protocol.six_dimensional_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    structural_extraction JSONB DEFAULT '{}'::jsonb,
    pattern_subtext JSONB DEFAULT '{}'::jsonb,
    strategic_synthesis JSONB DEFAULT '{}'::jsonb,
    narrative_integration JSONB DEFAULT '{}'::jsonb,
    solution_architecture JSONB DEFAULT '{}'::jsonb,
    human_needs_dynamics JSONB DEFAULT '{}'::jsonb,
    overall_score DECIMAL(3,2),
    analysis_version VARCHAR(10) DEFAULT '9.1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Protocol outputs
CREATE TABLE IF NOT EXISTS oracle_protocol.protocol_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    output_type VARCHAR(100) NOT NULL,
    content JSONB NOT NULL,
    file_path VARCHAR(500),
    format VARCHAR(20) DEFAULT 'json',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_id, output_type, version)
);

-- Decisions and agreements
CREATE TABLE IF NOT EXISTS oracle_protocol.decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    decision_id VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    made_by VARCHAR(255),
    rationale TEXT,
    related_actions JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    consensus_points JSONB DEFAULT '[]'::jsonb,
    implementation_plan JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Actions register
CREATE TABLE IF NOT EXISTS oracle_protocol.actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    action_id VARCHAR(50) NOT NULL,
    type VARCHAR(50) DEFAULT 'explicit', -- explicit, implicit
    description TEXT NOT NULL,
    assigned_to VARCHAR(255),
    due_date TIMESTAMP WITH TIME ZONE,
    priority VARCHAR(20) DEFAULT 'medium',
    tags JSONB DEFAULT '[]'::jsonb,
    implementation_velocity INTEGER, -- 1-10 scale
    exponential_potential INTEGER, -- 1-10 scale
    support_package JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Human needs analysis
CREATE TABLE IF NOT EXISTS oracle_protocol.human_needs_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    participant_id VARCHAR(255),
    certainty_score INTEGER CHECK (certainty_score >= 0 AND certainty_score <= 10),
    variety_score INTEGER CHECK (variety_score >= 0 AND variety_score <= 10),
    significance_score INTEGER CHECK (significance_score >= 0 AND significance_score <= 10),
    connection_score INTEGER CHECK (connection_score >= 0 AND connection_score <= 10),
    growth_score INTEGER CHECK (growth_score >= 0 AND growth_score <= 10),
    contribution_score INTEGER CHECK (contribution_score >= 0 AND contribution_score <= 10),
    need_interactions JSONB DEFAULT '{}'::jsonb,
    imbalances JSONB DEFAULT '[]'::jsonb,
    interventions JSONB DEFAULT '[]'::jsonb,
    privacy_level VARCHAR(20) DEFAULT 'team', -- individual, team, organization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Strategic framework alignments
CREATE TABLE IF NOT EXISTS oracle_protocol.strategic_alignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    framework_name VARCHAR(100) NOT NULL, -- SDGs, Doughnut Economy, Agreement Economy
    framework_version VARCHAR(20),
    alignment_score DECIMAL(3,2),
    aligned_elements JSONB DEFAULT '[]'::jsonb,
    gaps JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Pattern recognition results
CREATE TABLE IF NOT EXISTS oracle_protocol.patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    description TEXT,
    occurrences JSONB DEFAULT '[]'::jsonb,
    meetings JSONB DEFAULT '[]'::jsonb,
    confidence_score DECIMAL(3,2),
    intervention_protocols JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- AI processing jobs
CREATE TABLE IF NOT EXISTS ai_processing.processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type VARCHAR(100) NOT NULL,
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    processing_time INTEGER, -- in milliseconds
    ai_model VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Voice processing sessions
CREATE TABLE IF NOT EXISTS voice_processing.voice_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meeting_id UUID REFERENCES oracle_protocol.meetings(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    audio_data BYTEA,
    transcript TEXT,
    speaker_identification JSONB DEFAULT '{}'::jsonb,
    confidence_scores JSONB DEFAULT '{}'::jsonb,
    processing_metadata JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(50) DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- External integrations
CREATE TABLE IF NOT EXISTS integrations.integration_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    integration_type VARCHAR(100) NOT NULL, -- zapier, notion, dart, git
    config JSONB NOT NULL,
    credentials JSONB, -- encrypted
    status VARCHAR(50) DEFAULT 'active',
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Integration sync logs
CREATE TABLE IF NOT EXISTS integrations.sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    integration_config_id UUID REFERENCES integrations.integration_configs(id),
    sync_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    sync_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_meetings_organization_date ON oracle_protocol.meetings(organization_id, date_time);
CREATE INDEX IF NOT EXISTS idx_meetings_status ON oracle_protocol.meetings(status);
CREATE INDEX IF NOT EXISTS idx_transcripts_meeting ON oracle_protocol.conversation_transcripts(meeting_id);
CREATE INDEX IF NOT EXISTS idx_analysis_meeting ON oracle_protocol.six_dimensional_analysis(meeting_id);
CREATE INDEX IF NOT EXISTS idx_outputs_meeting_type ON oracle_protocol.protocol_outputs(meeting_id, output_type);
CREATE INDEX IF NOT EXISTS idx_decisions_meeting ON oracle_protocol.decisions(meeting_id);
CREATE INDEX IF NOT EXISTS idx_actions_meeting_status ON oracle_protocol.actions(meeting_id, status);
CREATE INDEX IF NOT EXISTS idx_human_needs_meeting ON oracle_protocol.human_needs_analysis(meeting_id);
CREATE INDEX IF NOT EXISTS idx_strategic_alignments_meeting ON oracle_protocol.strategic_alignments(meeting_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON oracle_protocol.patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON ai_processing.processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_voice_sessions_meeting ON voice_processing.voice_sessions(meeting_id);
CREATE INDEX IF NOT EXISTS idx_integration_configs_org_type ON integrations.integration_configs(organization_id, integration_type);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_meetings_title_search ON oracle_protocol.meetings USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_transcripts_content_search ON oracle_protocol.conversation_transcripts USING gin(to_tsvector('english', processed_transcript));
CREATE INDEX IF NOT EXISTS idx_decisions_description_search ON oracle_protocol.decisions USING gin(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_actions_description_search ON oracle_protocol.actions USING gin(to_tsvector('english', description));

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables with updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_meetings_updated_at BEFORE UPDATE ON oracle_protocol.meetings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transcripts_updated_at BEFORE UPDATE ON oracle_protocol.conversation_transcripts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analysis_updated_at BEFORE UPDATE ON oracle_protocol.six_dimensional_analysis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outputs_updated_at BEFORE UPDATE ON oracle_protocol.protocol_outputs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_decisions_updated_at BEFORE UPDATE ON oracle_protocol.decisions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_actions_updated_at BEFORE UPDATE ON oracle_protocol.actions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_human_needs_updated_at BEFORE UPDATE ON oracle_protocol.human_needs_analysis FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategic_alignments_updated_at BEFORE UPDATE ON oracle_protocol.strategic_alignments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON oracle_protocol.patterns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_processing_jobs_updated_at BEFORE UPDATE ON ai_processing.processing_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_voice_sessions_updated_at BEFORE UPDATE ON voice_processing.voice_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integration_configs_updated_at BEFORE UPDATE ON integrations.integration_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default data
INSERT INTO organizations (id, name, domain, settings) VALUES 
    (uuid_generate_v4(), 'Default Organization', 'localhost', '{"oracle_protocol_version": "9.1", "features": {"voice_processing": true, "ai_orchestration": true, "human_needs_analysis": true}}')
ON CONFLICT DO NOTHING;

-- Create default admin user
INSERT INTO users (id, email, name, role, preferences) VALUES 
    (uuid_generate_v4(), 'admin@intelligence-os.local', 'System Administrator', 'admin', '{"dashboard_layout": "default", "notification_preferences": {"email": true, "push": true}}')
ON CONFLICT DO NOTHING;