'use client';

import { useState, useEffect } from 'react';
import { 
  TreeStructure, 
  ClockCounterClockwise,
  ChatCircle,
  User,
  Wrench,
  Spinner,
  CaretRight,
  CaretDown
} from '@phosphor-icons/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getSessions, getSessionEvents, ApiError } from '@/lib/api';
import type { Session, TimelineEvent } from '@/lib/types';
import { toast } from 'sonner';
import { cn, formatRelativeTime, formatTokenCount } from '@/lib/utils';

export function SessionsView() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);
  const [sessionEvents, setSessionEvents] = useState<Record<string, TimelineEvent[]>>({});
  const [loadingEvents, setLoadingEvents] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const data = await getSessions(0, 50);
      setSessions(data.sessions);
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error('Failed to load sessions', {
          description: error.message,
        });
      } else {
        toast.error('Network error');
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleSession = async (sessionId: string) => {
    if (expandedSessionId === sessionId) {
      setExpandedSessionId(null);
      return;
    }

    setExpandedSessionId(sessionId);

    // Load events if not already loaded
    if (!sessionEvents[sessionId]) {
      setLoadingEvents({ ...loadingEvents, [sessionId]: true });
      try {
        const data = await getSessionEvents(sessionId);
        setSessionEvents({ ...sessionEvents, [sessionId]: data.timeline });
      } catch (error) {
        if (error instanceof ApiError) {
          toast.error('Failed to load session events', {
            description: error.message,
          });
        }
      } finally {
        setLoadingEvents({ ...loadingEvents, [sessionId]: false });
      }
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'user_message':
        return <User size={16} weight="bold" />;
      case 'assistant_message':
        return <ChatCircle size={16} weight="bold" />;
      case 'tool_use':
        return <Wrench size={16} weight="bold" />;
      default:
        return <ClockCounterClockwise size={16} weight="bold" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'user_message':
        return 'bg-blue-500';
      case 'assistant_message':
        return 'bg-green-500';
      case 'tool_use':
        return 'bg-orange-500';
      default:
        return 'bg-purple-500';
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner className="animate-spin text-teal-600 mb-4" size={32} />
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Loading sessions...
        </p>
      </div>
    );
  }

  if (sessions.length === 0) {
    return (
      <div className="flex flex-col gap-6">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
            Session Traces
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            View detailed execution traces for all sessions
          </p>
        </div>
        
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <TreeStructure size={48} className="text-zinc-400 mb-4" />
            <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
              No sessions found
            </p>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Sessions will appear here after conversations
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Session Traces
        </h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          View detailed execution traces for {sessions.length} sessions
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {sessions.map((session) => (
          <Card key={session.session_id} className="overflow-hidden">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSession(session.session_id)}
                      className="h-8 w-8 p-0"
                    >
                      {expandedSessionId === session.session_id ? (
                        <CaretDown size={20} weight="bold" />
                      ) : (
                        <CaretRight size={20} weight="bold" />
                      )}
                    </Button>
                    <TreeStructure size={20} className="text-teal-600" weight="bold" />
                    <CardTitle className="text-base font-mono">
                      {session.session_id.slice(0, 12)}...
                    </CardTitle>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 ml-10">
                    <Badge variant="outline">
                      {session.turn_count} turns
                    </Badge>
                    <Badge variant="outline">
                      {session.message_count} messages
                    </Badge>
                    <Badge variant="outline">
                      {formatTokenCount(session.total_tokens_in + session.total_tokens_out)} tokens
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {formatRelativeTime(session.first_timestamp)} → {formatRelativeTime(session.last_timestamp)}
                    </Badge>
                  </div>
                </div>
              </div>
            </CardHeader>

            {expandedSessionId === session.session_id && (
              <CardContent className="pt-0">
                {loadingEvents[session.session_id] ? (
                  <div className="flex items-center justify-center py-8">
                    <Spinner className="animate-spin text-teal-600" size={24} />
                  </div>
                ) : sessionEvents[session.session_id]?.length > 0 ? (
                  <div className="rounded-md bg-zinc-50 dark:bg-zinc-900 p-4">
                    <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 mb-3">
                      Event Timeline ({sessionEvents[session.session_id].length} events)
                    </h4>
                    
                    <div className="relative">
                      <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-zinc-200 dark:bg-zinc-800" />
                      
                      <div className="flex flex-col gap-2">
                        {sessionEvents[session.session_id].map((event, index) => (
                          <div key={index} className="relative pl-8">
                            <div
                              className={cn(
                                'absolute left-0 top-1.5 h-4 w-4 rounded-full flex items-center justify-center text-white',
                                getEventColor(event.type)
                              )}
                            >
                              {getEventIcon(event.type)}
                            </div>
                            
                            <div className="flex items-center gap-2 text-sm">
                              <span className="font-medium text-zinc-700 dark:text-zinc-300">
                                Turn {event.turn}
                              </span>
                              <span className="text-zinc-500 dark:text-zinc-400">•</span>
                              <span className="text-zinc-600 dark:text-zinc-400 text-xs">
                                {formatRelativeTime(event.timestamp)}
                              </span>
                              {event.tool_name && (
                                <>
                                  <span className="text-zinc-500 dark:text-zinc-400">•</span>
                                  <span className="font-mono text-xs text-zinc-700 dark:text-zinc-300">
                                    {event.tool_name}
                                  </span>
                                </>
                              )}
                              {event.latency_ms && (
                                <>
                                  <span className="text-zinc-500 dark:text-zinc-400">•</span>
                                  <span className="text-xs text-zinc-600 dark:text-zinc-400">
                                    {event.latency_ms}ms
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-sm text-zinc-600 dark:text-zinc-400">
                    No events found for this session
                  </div>
                )}
              </CardContent>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
