'use client';

import { useState, useEffect } from 'react';
import { 
  Brain, 
  Lightbulb, 
  BookOpen, 
  FileCode,
  Spinner
} from '@phosphor-icons/react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  getDecisions, 
  getConventions, 
  getLearnings, 
  getArtifacts,
  ApiError 
} from '@/lib/api';
import type { Decision, Convention, Learning, Artifact } from '@/lib/types';
import { toast } from 'sonner';
import { formatRelativeTime } from '@/lib/utils';

export function KnowledgeView() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [conventions, setConventions] = useState<Convention[]>([]);
  const [learnings, setLearnings] = useState<Learning[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('decisions');

  useEffect(() => {
    loadAllKnowledge();
  }, []);

  const loadAllKnowledge = async () => {
    setLoading(true);
    try {
      const [decisionsData, conventionsData, learningsData, artifactsData] = await Promise.all([
        getDecisions(0, 20),
        getConventions(0, 20),
        getLearnings(0, 20),
        getArtifacts(0, 20),
      ]);
      
      setDecisions(decisionsData.decisions);
      setConventions(conventionsData.conventions);
      setLearnings(learningsData.learnings);
      setArtifacts(artifactsData.artifacts);
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error('Failed to load knowledge', {
          description: error.message,
        });
      } else {
        toast.error('Network error');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner className="animate-spin text-teal-600 mb-4" size={32} />
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Loading knowledge base...
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Knowledge Browser
        </h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Explore decisions, conventions, learnings, and artifacts
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="decisions">
            <Lightbulb size={16} className="mr-2" />
            Decisions ({decisions.length})
          </TabsTrigger>
          <TabsTrigger value="conventions">
            <BookOpen size={16} className="mr-2" />
            Conventions ({conventions.length})
          </TabsTrigger>
          <TabsTrigger value="learnings">
            <Brain size={16} className="mr-2" />
            Learnings ({learnings.length})
          </TabsTrigger>
          <TabsTrigger value="artifacts">
            <FileCode size={16} className="mr-2" />
            Artifacts ({artifacts.length})
          </TabsTrigger>
        </TabsList>

        {/* Decisions Tab */}
        <TabsContent value="decisions" className="mt-6">
          {decisions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Lightbulb size={48} className="text-zinc-400 mb-4" />
                <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                  No decisions recorded
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {decisions.map((decision, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-base mb-2">
                          {decision.question}
                        </CardTitle>
                        <div className="flex flex-wrap gap-2">
                          {decision.topics.map((topic) => (
                            <Badge key={topic} variant="outline">
                              {topic}
                            </Badge>
                          ))}
                          <Badge variant="outline" className="text-xs">
                            {formatRelativeTime(decision.decided_at)}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                        Decision:
                      </p>
                      <p className="text-sm text-zinc-700 dark:text-zinc-300">
                        {decision.decision}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                        Rationale:
                      </p>
                      <p className="text-sm text-zinc-700 dark:text-zinc-300">
                        {decision.rationale}
                      </p>
                    </div>
                    {decision.alternatives.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-1">
                          Alternatives considered:
                        </p>
                        <ul className="list-disc list-inside space-y-1">
                          {decision.alternatives.map((alt, i) => (
                            <li key={i} className="text-sm text-zinc-700 dark:text-zinc-300">
                              {alt}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Conventions Tab */}
        <TabsContent value="conventions" className="mt-6">
          {conventions.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BookOpen size={48} className="text-zinc-400 mb-4" />
                <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                  No conventions recorded
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {conventions.map((convention, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-base flex-1">
                        {convention.content}
                      </CardTitle>
                      <Badge 
                        variant={convention.confidence >= 0.8 ? 'default' : 'outline'}
                        className="shrink-0"
                      >
                        {(convention.confidence * 100).toFixed(0)}% confidence
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {convention.topics.map((topic) => (
                        <Badge key={topic} variant="outline">
                          {topic}
                        </Badge>
                      ))}
                      <Badge variant="outline" className="text-xs">
                        {formatRelativeTime(convention.created_at)}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Learnings Tab */}
        <TabsContent value="learnings" className="mt-6">
          {learnings.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Brain size={48} className="text-zinc-400 mb-4" />
                <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                  No learnings recorded
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {learnings.map((learning, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-base flex-1">
                        {learning.pattern}
                      </CardTitle>
                      <div className="flex gap-2 shrink-0">
                        <Badge variant="outline">
                          {learning.category}
                        </Badge>
                        <Badge 
                          variant={learning.confidence >= 0.8 ? 'default' : 'outline'}
                        >
                          {(learning.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                      <span>Learned from {learning.learned_from.length} sessions</span>
                      <span>•</span>
                      <span>{formatRelativeTime(learning.created_at)}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Artifacts Tab */}
        <TabsContent value="artifacts" className="mt-6">
          {artifacts.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileCode size={48} className="text-zinc-400 mb-4" />
                <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
                  No artifacts recorded
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {artifacts.map((artifact, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-base font-mono mb-1">
                          {artifact.path}
                        </CardTitle>
                        <CardDescription>
                          {artifact.description}
                        </CardDescription>
                      </div>
                      <Badge variant="outline" className="shrink-0">
                        {artifact.type}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {artifact.topics.map((topic) => (
                        <Badge key={topic} variant="outline">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
