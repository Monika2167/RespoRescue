import React, { useState } from "react";
import { HelpCircle, BookOpen, Search, ChevronDown, ChevronUp, Bot, Sparkles } from "lucide-react";
import { Card } from "../components/common/Card";
import { Badge } from "../components/common/Badge";

export const HelpAssistant = () => {
  const [openFaq, setOpenFaq] = useState(null);

  const faqs = [
    {
      q: "How do I connect GitHub to RepoRescue?",
      a: "Navigate to Dashboard or Settings, click 'Connect GitHub Account', and authorize through GitHub OAuth. Alternatively, enter a Personal Access Token with 'repo' scope directly in Settings. RepoRescue will automatically query your authorized repositories.",
    },
    {
      q: "What is Repository Health and how is it forecast?",
      a: "Repository Health forecasting utilizes a Ridge Regression time-series model (alpha=100.0) trained on 25 temporal features. It forecasts the 7-day average open PR and issue backlog trajectory based on historical commit and backlog patterns.",
    },
    {
      q: "How does PR Bottleneck Prediction work?",
      a: "The Bottleneck model is a Scaled Combined Logistic Regression classifier trained across 400 features (16 structured 24h code features and 384 MiniLM semantic text embeddings). It predicts whether a PR is likely to remain unresolved beyond 7 days using a calibrated 0.57 threshold.",
    },
    {
      q: "What does Knowledge Concentration mean?",
      a: "Knowledge concentration measures the distribution of code modifications across files. A file with high concentration (or single-contributor flag) indicates that one author accounts for over 80% of historical contributions, representing maintenance and bus-factor vulnerability.",
    },
    {
      q: "What is the difference between Repository AI and Help AI?",
      a: "The Repository AI Assistant is strictly scoped to the active repository workspace and answers questions using real evidence from your PR analyses and graph mining. This Help Center explains how the overall RepoRescue platform, models, and metrics function.",
    },
    {
      q: "Why does RepoRescue never display mock or sample data?",
      a: "Per RepoRescue's foundational software intelligence architecture, all risk scores, forecasts, and graph relations must come from real authenticated repositories. Fabricated data is strictly prohibited to maintain trustworthiness and integrity.",
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl">
      <div className="border-b border-slate-800/80 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <HelpCircle className="w-6 h-6 text-indigo-400" />
          Application Documentation & Help Assistant
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Learn how RepoRescue models, graph algorithms, and repository workflows operate.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card title="Bottleneck Model" subtitle="Decision Threshold: 0.57">
          <p className="text-xs text-slate-300 leading-relaxed">
            Scaled Combined Logistic Regression evaluating lines added/deleted, author churn, commit count, and NLP text semantics.
          </p>
        </Card>

        <Card title="Health Model" subtitle="Ridge Regression (alpha=100.0)">
          <p className="text-xs text-slate-300 leading-relaxed">
            Time-series backlog forecasting evaluating 25 temporal features to project 7-day average open PR backlog.
          </p>
        </Card>

        <Card title="Graph Mining" subtitle="Topology & Propagation">
          <p className="text-xs text-slate-300 leading-relaxed">
            Bipartite relationship graph and co-change frequency matrix determining knowledge concentration and cascading change risk.
          </p>
        </Card>
      </div>

      <Card title="Frequently Asked Questions & Platform Concepts">
        <div className="divide-y divide-slate-800/80">
          {faqs.map((faq, idx) => (
            <div key={idx} className="py-3.5">
              <button
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                className="w-full flex items-center justify-between text-left text-xs font-semibold text-slate-200 hover:text-indigo-400 transition"
              >
                <span>{faq.q}</span>
                {openFaq === idx ? (
                  <ChevronUp className="w-4 h-4 text-indigo-400 shrink-0" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" />
                )}
              </button>
              {openFaq === idx && (
                <p className="mt-2 text-xs text-slate-400 leading-relaxed animate-fade-in pl-1">
                  {faq.a}
                </p>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
