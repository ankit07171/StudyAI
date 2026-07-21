"use client";

import { useEffect, useState, useRef } from "react";
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
import { subjectsAPI , filesAPI } from "@/lib/api";
import { toast } from "sonner";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// API functions for new endpoints
const quizAPI = {
  generate: async (subjectId: string, data: any) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/quiz/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ ...data, subject_id: subjectId }),
    });
    if (!response.ok) throw new Error("Failed to generate quiz");
    return response.json();
  },
  getAll: async (subjectId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/quiz/subject/${subjectId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch quizzes");
    return response.json();
  },
  getQuestions: async (quizId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/quiz/${quizId}/questions`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch quiz questions");
    return response.json();
  },
};

const notesAPI = {
  generate: async (subjectId: string, data: any) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/notes/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ ...data, subject_id: subjectId }),
    });
    if (!response.ok) throw new Error("Failed to generate notes");
    return response.json();
  },
  getAll: async (subjectId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/notes/subject/${subjectId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch notes");
    return response.json();
  },
  getOne: async (noteId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/notes/${noteId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch note");
    return response.json();
  },
};

const questionsAPI = {
  generate: async (subjectId: string, data: any) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/questions/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ ...data, subject_id: subjectId }),
    });
    if (!response.ok) throw new Error("Failed to generate questions");
    return response.json();
  },
  getAll: async (subjectId: string, filters?: any) => {
    const token = localStorage.getItem("token");
    const params = new URLSearchParams(filters);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/questions/subject/${subjectId}?${params}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch questions");
    return response.json();
  },
  getOne: async (questionId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/questions/${questionId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch question");
    return response.json();
  },
};

const chatAPI = {
  sendMessage: async (subjectId: string, message: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ subject_id: subjectId, message }),
    });
    if (!response.ok) throw new Error("Failed to send message");
    return response.json();
  },
  getHistory: async (subjectId: string) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat/subject/${subjectId}`, {
      headers: { "Authorization": `Bearer ${token}` },
    });
    if (!response.ok) throw new Error("Failed to fetch chat history");
    return response.json();
  },
};

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
  const [activeTab, setActiveTab] = useState<"chat" | "notes" | "quiz" | "flashcards" | "questions">("chat");
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<any[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  
  // Notes state
  const [notes, setNotes] = useState<any[]>([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [selectedNote, setSelectedNote] = useState<any>(null);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: "", note_type: "complete" });
  
  // Quiz state
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState<any>(null);
  const [quizQuestions, setQuizQuestions] = useState<any[]>([]);
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [quizForm, setQuizForm] = useState({ title: "", question_count: 10 });
  
  // Questions state
  const [importantQuestions, setImportantQuestions] = useState<any[]>([]);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [questionForm, setQuestionForm] = useState({ question_count: 15 });

  useEffect(() => {
    loadSubject();
  }, [subjectId]);

const [uploading, setUploading] = useState(false);
const [dragActive, setDragActive] = useState(false);
const fileInputRef = useRef<HTMLInputElement>(null);

const handleFiles = async (files: FileList | null) => {
  if (!files || files.length === 0) return;

  for (const file of Array.from(files)) {
    if (file.type !== "application/pdf") {
      toast.error(`${file.name} is not a PDF`);
      continue;
    }
    if (file.size > 50 * 1024 * 1024) {
      toast.error(`${file.name} exceeds 50MB`);
      continue;
    }

    setUploading(true);
    try {
      await filesAPI.upload(subjectId, file);
      toast.success(`${file.name} uploaded`);
      await loadSubject(); // refresh stats (total_pdfs etc.)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || `Failed to upload ${file.name}`);
    } finally {
      setUploading(false);
    }
  }
};

const handleDrop = (e: React.DragEvent) => {
  e.preventDefault();
  setDragActive(false);
  handleFiles(e.dataTransfer.files);
};

 const loadSubject = async () => {
  try {
    const data = await subjectsAPI.getOne(subjectId);
    setSubject(data);
  } catch (error: any) {
    console.error("Subject load error:", error.response?.status, error.response?.data, error.message);
    toast.error(error.response?.data?.detail || "Failed to load subject");
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

  // Chat handlers
  const loadChatHistory = async () => {
    try {
      const history = await chatAPI.getHistory(subjectId);
      setChatMessages(history);
    } catch (error: any) {
      console.error("Failed to load chat history:", error);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;
    
    setChatLoading(true);
    try {
      const response = await chatAPI.sendMessage(subjectId, chatInput);
      setChatMessages([...chatMessages, { role: "user", message: chatInput }, response]);
      setChatInput("");
    } catch (error: any) {
      toast.error(error.message || "Failed to send message");
    } finally {
      setChatLoading(false);
    }
  };

  // Notes handlers
  const loadNotes = async () => {
    setNotesLoading(true);
    try {
      const data = await notesAPI.getAll(subjectId);
      setNotes(data);
    } catch (error: any) {
      console.error("Failed to load notes:", error);
    } finally {
      setNotesLoading(false);
    }
  };

  const handleGenerateNotes = async () => {
    if (!noteForm.title.trim()) {
      toast.error("Please enter a title for the notes");
      return;
    }
    
    setNotesLoading(true);
    try {
      await notesAPI.generate(subjectId, noteForm);
      toast.success("Notes generated successfully!");
      setShowNoteModal(false);
      setNoteForm({ title: "", note_type: "complete" });
      loadNotes();
      loadSubject();
    } catch (error: any) {
      toast.error(error.message || "Failed to generate notes");
    } finally {
      setNotesLoading(false);
    }
  };

  const handleViewNote = async (noteId: string) => {
    try {
      const note = await notesAPI.getOne(noteId);
      setSelectedNote(note);
      setShowNoteModal(true);
    } catch (error: any) {
      toast.error("Failed to load note");
    }
  };

  // Quiz handlers
  const loadQuizzes = async () => {
    setQuizLoading(true);
    try {
      const data = await quizAPI.getAll(subjectId);
      setQuizzes(data);
    } catch (error: any) {
      console.error("Failed to load quizzes:", error);
    } finally {
      setQuizLoading(false);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizForm.title.trim()) {
      toast.error("Please enter a title for the quiz");
      return;
    }
    
    setQuizLoading(true);
    try {
      await quizAPI.generate(subjectId, quizForm);
      toast.success("Quiz generated successfully!");
      setShowQuizModal(false);
      setQuizForm({ title: "", question_count: 10 });
      loadQuizzes();
      loadSubject();
    } catch (error: any) {
      toast.error(error.message || "Failed to generate quiz");
    } finally {
      setQuizLoading(false);
    }
  };

  const handleViewQuiz = async (quizId: string) => {
    try {
      const questions = await quizAPI.getQuestions(quizId);
      const quiz = quizzes.find(q => q.id === quizId);
      setSelectedQuiz(quiz);
      setQuizQuestions(questions);
      setShowQuizModal(true);
    } catch (error: any) {
      toast.error("Failed to load quiz");
    }
  };

  // Important Questions handlers
  const loadImportantQuestions = async () => {
    setQuestionsLoading(true);
    try {
      const data = await questionsAPI.getAll(subjectId);
      setImportantQuestions(data);
    } catch (error: any) {
      console.error("Failed to load questions:", error);
    } finally {
      setQuestionsLoading(false);
    }
  };

  const handleGenerateQuestions = async () => {
    setQuestionsLoading(true);
    try {
      await questionsAPI.generate(subjectId, questionForm);
      toast.success("Important questions generated successfully!");
      setShowQuestionModal(false);
      setQuestionForm({ question_count: 15 });
      loadImportantQuestions();
    } catch (error: any) {
      toast.error(error.message || "Failed to generate questions");
    } finally {
      setQuestionsLoading(false);
    }
  };

  const handleViewQuestion = async (questionId: string) => {
    try {
      const question = await questionsAPI.getOne(questionId);
      setSelectedQuestion(question);
      setShowQuestionModal(true);
    } catch (error: any) {
      toast.error("Failed to load question");
    }
  };

  useEffect(() => {
    if (activeTab === "notes") loadNotes();
    if (activeTab === "quiz") loadQuizzes();
    if (activeTab === "questions") loadImportantQuestions();
    if (activeTab === "chat") loadChatHistory();
  }, [activeTab]);

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
          <div
  onClick={() => fileInputRef.current?.click()}
  onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
  onDragLeave={() => setDragActive(false)}
  onDrop={handleDrop}
  className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
    dragActive ? "border-blue-500 bg-blue-500/5" : "border-slate-700 hover:border-blue-500"
  }`}
>
  <input
    ref={fileInputRef}
    type="file"
    accept="application/pdf"
    multiple
    className="hidden"
    onChange={(e) => handleFiles(e.target.files)}
  />
  <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4" />
  <p className="text-slate-400 mb-2">Drag and drop PDF files here, or click to browse</p>
  <p className="text-sm text-slate-500">Maximum file size: 50MB</p>
  <button
    type="button"
    disabled={uploading}
    onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
    className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
  >
    {uploading ? "Uploading..." : "Select Files"}
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
          <button
            onClick={() => setActiveTab("questions")}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === "questions"
                ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg shadow-blue-500/50"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <FileText className="w-4 h-4" />
            Important Questions
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
                <div className="space-y-4">
                  <div className="h-96 overflow-y-auto space-y-4 p-4 bg-slate-900/50 rounded-xl">
                    {chatMessages.length === 0 ? (
                      <div className="text-center py-16">
                        <MessageSquare className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">Start Chatting with Your PDFs</h3>
                        <p className="text-slate-400">Upload PDF files first to start chatting</p>
                      </div>
                    ) : (
                      chatMessages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                          <div className={`max-w-[80%] p-3 rounded-xl ${
                            msg.role === "user" 
                              ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white" 
                              : "bg-slate-800 text-white"
                          }`}>
                            {msg.message || msg.content}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                      placeholder="Ask a question about your PDFs..."
                      className="flex-1 px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                      disabled={chatLoading || subject.total_pdfs === 0}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={chatLoading || subject.total_pdfs === 0}
                      className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
                    >
                      {chatLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Send"}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === "notes" && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">Generated Notes</h3>
                    <button
                      onClick={() => setShowNoteModal(true)}
                      className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all"
                    >
                      Generate Notes
                    </button>
                  </div>
                  {notesLoading ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
                    </div>
                  ) : notes.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                      No notes generated yet. Click "Generate Notes" to create your first set.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {notes.map((note) => (
                        <div
                          key={note.id}
                          onClick={() => handleViewNote(note.id)}
                          className="p-4 bg-slate-800 rounded-xl hover:bg-slate-700 cursor-pointer transition-colors"
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-medium text-white">{note.title}</h4>
                              <p className="text-sm text-slate-400">{note.note_type}</p>
                            </div>
                            <span className="text-xs text-slate-500">
                              {new Date(note.generated_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === "quiz" && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">Quizzes</h3>
                    <button
                      onClick={() => setShowQuizModal(true)}
                      className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all"
                    >
                      Generate Quiz
                    </button>
                  </div>
                  {quizLoading ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
                    </div>
                  ) : quizzes.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                      No quizzes generated yet. Click "Generate Quiz" to create your first quiz.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {quizzes.map((quiz) => (
                        <div
                          key={quiz.id}
                          onClick={() => handleViewQuiz(quiz.id)}
                          className="p-4 bg-slate-800 rounded-xl hover:bg-slate-700 cursor-pointer transition-colors"
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <h4 className="font-medium text-white">{quiz.title}</h4>
                              <p className="text-sm text-slate-400">{quiz.question_count} questions • {quiz.total_marks} marks</p>
                            </div>
                            <span className="text-xs text-slate-500">
                              {new Date(quiz.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === "questions" && (
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-white">Important Questions</h3>
                    <button
                      onClick={() => setShowQuestionModal(true)}
                      className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all"
                    >
                      Generate Questions
                    </button>
                  </div>
                  {questionsLoading ? (
                    <div className="text-center py-8">
                      <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
                    </div>
                  ) : importantQuestions.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                      No important questions generated yet. Click "Generate Questions" to create your first set.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {importantQuestions.map((q) => (
                        <div
                          key={q.id}
                          onClick={() => handleViewQuestion(q.id)}
                          className="p-4 bg-slate-800 rounded-xl hover:bg-slate-700 cursor-pointer transition-colors"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h4 className="font-medium text-white mb-1">{q.question_text}</h4>
                              <div className="flex gap-2 text-xs text-slate-400">
                                <span className="px-2 py-1 bg-slate-700 rounded">{q.marks} marks</span>
                                <span className="px-2 py-1 bg-slate-700 rounded">{q.difficulty}</span>
                                <span className="px-2 py-1 bg-slate-700 rounded">{q.category}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
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

      {/* Note Generation Modal */}
      {showNoteModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Generate Notes</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Title</label>
                <input
                  type="text"
                  value={noteForm.title}
                  onChange={(e) => setNoteForm({ ...noteForm, title: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., Complete Chapter Notes"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Type</label>
                <select
                  value={noteForm.note_type}
                  onChange={(e) => setNoteForm({ ...noteForm, note_type: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="complete">Complete Notes</option>
                  <option value="summary">Summary</option>
                  <option value="formula_sheet">Formula Sheet</option>
                  <option value="keyword">Keywords</option>
                </select>
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowNoteModal(false)}
                  className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateNotes}
                  disabled={notesLoading}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
                >
                  {notesLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : "Generate"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Note View Modal */}
      {selectedNote && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-white">{selectedNote.title}</h2>
              <button onClick={() => {setSelectedNote(null);setShowNoteModal(false);}} className="text-slate-400 hover:text-white">
  ✕
</button>
            </div>
            <div className="prose prose-invert max-w-none text-white">
              <div className="whitespace-pre-wrap">{selectedNote.content}</div>
            </div>
          </div>
        </div>
      )}

      {/* Quiz Generation Modal */}
      {showQuizModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Generate Quiz</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Title</label>
                <input
                  type="text"
                  value={quizForm.title}
                  onChange={(e) => setQuizForm({ ...quizForm, title: e.target.value })}
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                  placeholder="e.g., Chapter 1 Quiz"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Number of Questions</label>
                <input
                  type="number"
                  value={quizForm.question_count}
                  onChange={(e) => setQuizForm({ ...quizForm, question_count: parseInt(e.target.value) })}
                  min="1"
                  max="50"
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowQuizModal(false)}
                  className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateQuiz}
                  disabled={quizLoading}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
                >
                  {quizLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : "Generate"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Question Generation Modal */}
      {showQuestionModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Generate Important Questions</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Number of Questions</label>
                <input
                  type="number"
                  value={questionForm.question_count}
                  onChange={(e) => setQuestionForm({ ...questionForm, question_count: parseInt(e.target.value) })}
                  min="1"
                  max="50"
                  className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700 rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowQuestionModal(false)}
                  className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateQuestions}
                  disabled={questionsLoading}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50"
                >
                  {questionsLoading ? <Loader2 className="w-5 h-5 animate-spin mx-auto" /> : "Generate"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
