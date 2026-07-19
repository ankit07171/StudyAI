"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Upload,
  MessageSquare,
  FileText,
  Award,
  BookOpen,
  Loader2,
  Brain,
  Trash2,
  Edit,
} from "lucide-react";
import { subjectsAPI } from "@/lib/api";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Subject {
  id: string;
  name: string;
  code?: string;
  semester?: string;
  description?: string;
  total_pdfs: number;
  notes_count: number;
  quizzes_count: number;
  flashcards_count: number;
  chat_messages_count: number;
}

export default function SubjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const subjectId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [subject, setSubject] = useState<Subject | null>(null);
  const [activeTab, setActiveTab] = useState<"chat" | "notes" | "quiz" | "flashcards">("chat");

  useEffect(() => {
    loadSubject();
  }, [subjectId]);

  const loadSubject = async () => {
    try {
      const data = await subjectsAPI.getOne(subjectId);
      setSubject(data);
      // console.log();
      
    } catch (error: any) {
      toast.error("Failed to load subject");
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this subject? This action cannot be undone.")) {
      return;
    }

    try {
      await subjectsAPI.delete(subjectId);
      toast.success("Subject deleted successfully");
      router.push("/dashboard");
    } catch (error: any) {
      toast.error("Failed to delete subject");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!subject) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-slate-400" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">{subject.name}</h1>
                  <p className="text-sm text-slate-400">
                    {subject.code && `${subject.code} • `}
                    {subject.semester || "No semester"}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
                <Edit className="w-5 h-5 text-slate-400" />
              </button>
              <button
                onClick={handleDelete}
                className="p-2 hover:bg-red-500/10 rounded-lg transition-colors"
              >
                <Trash2 className="w-5 h-5 text-red-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <BookOpen className="w-8 h-8 text-blue-500" />
                <div>
                  <div className="text-2xl font-bold text-white">{subject.total_pdfs}</div>
                  <div className="text-sm text-slate-400">PDFs</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <FileText className="w-8 h-8 text-green-500" />
                <div>
                  <div className="text-2xl font-bold text-white">{subject.notes_count}</div>
                  <div className="text-sm text-slate-400">Notes</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Award className="w-8 h-8 text-purple-500" />
                <div>
                  <div className="text-2xl font-bold text-white">{subject.quizzes_count}</div>
                  <div className="text-sm text-slate-400">Quizzes</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <MessageSquare className="w-8 h-8 text-orange-500" />
                <div>
                  <div className="text-2xl font-bold text-white">{subject.chat_messages_count}</div>
                  <div className="text-sm text-slate-400">Chats</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Upload Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="w-5 h-5" />
              Upload Study Materials
            </CardTitle>
            <CardDescription>Upload PDF files to chat with and generate study materials</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:border-blue-500 transition-colors cursor-pointer">
              <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400 mb-2">Drag and drop PDF files here, or click to browse</p>
              <p className="text-sm text-slate-500">Maximum file size: 50MB</p>
              <button className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                Select Files
              </button>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === "chat"
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab("notes")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === "notes"
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <FileText className="w-4 h-4" />
            Notes
          </button>
          <button
            onClick={() => setActiveTab("quiz")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === "quiz"
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <Award className="w-4 h-4" />
            Quiz
          </button>
          <button
            onClick={() => setActiveTab("flashcards")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === "flashcards"
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <BookOpen className="w-4 h-4" />
            Flashcards
          </button>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent className="p-8">
              {activeTab === "chat" && (
                <div className="text-center py-16">
                  <MessageSquare className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Start Chatting with Your PDFs</h3>
                  <p className="text-slate-400 mb-6">Upload PDF files first to start chatting</p>
                  <p className="text-sm text-slate-500">Coming soon: AI-powered chat interface</p>
                </div>
              )}

              {activeTab === "notes" && (
                <div className="text-center py-16">
                  <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Generate Study Notes</h3>
                  <p className="text-slate-400 mb-6">AI will generate comprehensive notes from your PDFs</p>
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                    Generate Notes (Coming Soon)
                  </button>
                </div>
              )}

              {activeTab === "quiz" && (
                <div className="text-center py-16">
                  <Award className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Practice with Quizzes</h3>
                  <p className="text-slate-400 mb-6">AI-generated quizzes based on your study materials</p>
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                    Generate Quiz (Coming Soon)
                  </button>
                </div>
              )}

              {activeTab === "flashcards" && (
                <div className="text-center py-16">
                  <BookOpen className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Study with Flashcards</h3>
                  <p className="text-slate-400 mb-6">Spaced repetition flashcards for better retention</p>
                  <button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all">
                    Generate Flashcards (Coming Soon)
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
