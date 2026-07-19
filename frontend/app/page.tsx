"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { 
  BookOpen, 
  Brain, 
  Sparkles, 
  FileText, 
  MessageSquare, 
  Award,
  ArrowRight
} from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: Brain,
      title: "AI-Powered Chat",
      description: "Ask questions and get instant answers from your study materials"
    },
    {
      icon: FileText,
      title: "Smart Notes",
      description: "Auto-generate comprehensive notes from your PDFs"
    },
    {
      icon: Award,
      title: "Quiz Generator",
      description: "Create practice quizzes to test your knowledge"
    },
    {
      icon: Sparkles,
      title: "Flashcards",
      description: "Generate flashcards with spaced repetition"
    },
    {
      icon: BookOpen,
      title: "Important Questions",
      description: "Get exam-focused questions with model answers"
    },
    {
      icon: MessageSquare,
      title: "Revision Sheets",
      description: "One-page guides for quick last-minute revision"
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center space-y-8"
        >
          {/* Logo/Title */}
          <div className="flex items-center justify-center space-x-3">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
              <Brain className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI Study Assistant
            </h1>
          </div>

          {/* Subtitle */}
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Your intelligent companion for exam preparation. Upload PDFs, chat with AI, 
            and ace your exams with personalized study materials.
          </p>

          {/* CTA Buttons */}
          <div className="flex items-center justify-center gap-4">
            <Link href="/auth/register">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold flex items-center gap-2 shadow-lg shadow-blue-500/50"
              >
                Get Started <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            
            <Link href="/auth/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-slate-800/50 backdrop-blur-sm text-white rounded-xl font-semibold border border-slate-700 hover:border-slate-600"
              >
                Sign In
              </motion.button>
            </Link>
          </div>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ y: -5 }}
              className="p-6 bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700 hover:border-blue-500/50 transition-all"
            >
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-slate-400">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 text-center"
        >
          <div>
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              10+
            </div>
            <div className="text-slate-400 mt-2">PDFs per Subject</div>
          </div>
          <div>
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              AI-Powered
            </div>
            <div className="text-slate-400 mt-2">Study Materials</div>
          </div>
          <div>
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              100%
            </div>
            <div className="text-slate-400 mt-2">Free to Use</div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
