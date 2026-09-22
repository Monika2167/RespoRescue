import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Sparkles, Send, Bot, User, AlertCircle, CheckCircle2, Layers, Share2 } from "lucide-react";
import { repositoryService } from "../services/repository";
import { useRepo } from "../context/RepoContext";
import { RepoWorkspaceHeader } from "../components/repository/RepoWorkspaceHeader";
import { RepoWorkspaceNav } from "../components/repository/RepoWorkspaceNav";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";

export const RepositoryAssistant = () => {
  const { repositoryId } = useParams();
  const { selectedRepo } = useRepo();

  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hello! I am your RepoRescue repository assistant. I can explain bottleneck predictions, knowledge concentration, and health forecasts using real evidence from this repository.",
      model_evidence: [],
      graph_evidence: [],
      repository_data: {},
    },
  ]);

  const suggestionChips = [
    "Why is this repository showing high bottleneck risk?",
    "Which pull requests are predicted to become bottlenecks?",
    "Which files have the highest knowledge concentration?",
    "Which developers are concentrated around critical files?",
    "What could increase repository change risk?",
    "What does the health forecast indicate?",
    "What would happen if contributor capacity increased?",
  ];

  const handleSend = async (question) => {
    const q = question || query;
    if (!q.trim()) return;

    const userMessage = { sender: "user", text: q };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");
    setLoading(true);

    try {
      const res = await repositoryService.askAssistant(repositoryId, q);
      const assistantMessage = {
        sender: "assistant",
        text: res.explanation || "No explanation returned.",
        model_evidence: res.model_evidence || [],
        graph_evidence: res.graph_evidence || [],
        repository_data: res.repository_data || {},
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = {
        sender: "assistant",
        text: err.message || "I don't have enough repository data to answer that yet.",
        model_evidence: [],
        graph_evidence: [],
        repository_data: {},
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <RepoWorkspaceHeader repository={selectedRepo} />
      <RepoWorkspaceNav />

      <div className="border-b border-slate-800/80 pb-4">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          RepoRescue AI
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Your repository intelligence assistant — strictly grounded in real model predictions and graph evidence.
        </p>
      </div>

      {/* Suggestion Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <span className="text-xs text-slate-500 font-medium shrink-0">Ask about:</span>
        {suggestionChips.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip)}
            className="px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800 text-xs text-slate-300 hover:text-white transition whitespace-nowrap"
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Conversation Thread */}
      <Card noPadding className="flex flex-col h-[520px]">
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-3xl ${
                m.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  m.sender === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 border border-slate-700 text-indigo-400"
                }`}
              >
                {m.sender === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div
                className={`rounded-2xl p-4 text-xs leading-relaxed ${
                  m.sender === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-900 border border-slate-800 text-slate-200"
                }`}
              >
                <div className="font-sans mb-1">{m.text}</div>

                {/* Clearly partitioned evidence sections */}
                {m.model_evidence && m.model_evidence.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800 space-y-1.5">
                    <div className="text-[10px] uppercase font-bold text-indigo-400 tracking-wider flex items-center gap-1">
                      <Layers className="w-3 h-3" />
                      Model Evidence
                    </div>
                    {m.model_evidence.map((ev, i) => (
                      <div key={i} className="text-[11px] text-slate-300 font-mono bg-black/30 p-1.5 rounded">
                        • {ev}
                      </div>
                    ))}
                  </div>
                )}

                {m.graph_evidence && m.graph_evidence.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800 space-y-1.5">
                    <div className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider flex items-center gap-1">
                      <Share2 className="w-3 h-3" />
                      Graph Evidence
                    </div>
                    {m.graph_evidence.map((gev, i) => (
                      <div key={i} className="text-[11px] text-slate-300 font-mono bg-black/30 p-1.5 rounded">
                        • {gev}
                      </div>
                    ))}
                  </div>
                )}

                {m.repository_data && Object.keys(m.repository_data).length > 0 && (
                  <div className="mt-2 text-[10px] text-slate-500 font-mono">
                    Grounded in: {m.repository_data.repository_name || selectedRepo?.name} (PRs on record: {m.repository_data.total_analyzed_prs ?? 0})
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 mr-auto max-w-xl">
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 text-indigo-400 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 animate-pulse" />
              </div>
              <div className="rounded-2xl p-3.5 bg-slate-900 border border-slate-800 text-xs text-slate-400">
                Evaluating repository evidence...
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-3 border-t border-slate-800/80 bg-slate-900/50 flex items-center gap-2"
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask RepoRescue AI about this repository..."
            className="flex-1 px-4 py-2 text-xs bg-slate-900 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <Button
            type="submit"
            variant="primary"
            size="sm"
            icon={Send}
            loading={loading}
            disabled={!query.trim()}
          >
            Send
          </Button>
        </form>
      </Card>
    </div>
  );
};
