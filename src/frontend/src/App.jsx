import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { 
  Mic, 
  MicOff, 
  Users, 
  Brain, 
  BarChart3, 
  Settings, 
  Play, 
  Pause, 
  Square,
  Volume2,
  VolumeX,
  MessageSquare,
  FileText,
  Target,
  Lightbulb,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  Eye,
  Heart,
  Shield
} from 'lucide-react'
import './App.css'

function App() {
  // Voice and Recording State
  const [isListening, setIsListening] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [voiceText, setVoiceText] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  
  // Meeting State
  const [meetingActive, setMeetingActive] = useState(false)
  const [meetingDuration, setMeetingDuration] = useState(0)
  const [participants, setParticipants] = useState(['Alex Chen', 'Sarah Johnson', 'Mike Rodriguez'])
  const [transcript, setTranscript] = useState('')
  
  // Analysis State
  const [analysisData, setAnalysisData] = useState(null)
  const [analysisLoading, setAnalysisLoading] = useState(false)
  const [realTimeInsights, setRealTimeInsights] = useState([])
  
  // UI State
  const [activeTab, setActiveTab] = useState('dashboard')
  const [notifications, setNotifications] = useState([])
  
  // Refs
  const recognitionRef = useRef(null)
  const meetingTimerRef = useRef(null)

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'
      
      recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
        
        if (finalTranscript) {
          setTranscript(prev => prev + finalTranscript + ' ')
          processVoiceInput(finalTranscript)
        }
        setVoiceText(interimTranscript)
      }
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }
      
      recognitionRef.current = recognition
    }
  }, [])

  // Meeting Timer
  useEffect(() => {
    if (meetingActive) {
      meetingTimerRef.current = setInterval(() => {
        setMeetingDuration(prev => prev + 1)
      }, 1000)
    } else {
      clearInterval(meetingTimerRef.current)
    }
    
    return () => clearInterval(meetingTimerRef.current)
  }, [meetingActive])

  // Process voice input with Oracle AI
  const processVoiceInput = async (text) => {
    try {
      const response = await fetch('/api/oracle/voice-process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          session_id: 'current-meeting'
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setAiResponse(data.response)
        addNotification('AI Insight', data.response, 'info')
      }
    } catch (error) {
      console.error('Voice processing error:', error)
    }
  }

  // Toggle voice listening
  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
    } else {
      recognitionRef.current?.start()
      setIsListening(true)
    }
  }

  // Start/Stop Meeting
  const toggleMeeting = () => {
    if (meetingActive) {
      setMeetingActive(false)
      setMeetingDuration(0)
      if (transcript) {
        performOracleAnalysis()
      }
    } else {
      setMeetingActive(true)
      setTranscript('')
      setRealTimeInsights([])
    }
  }

  // Perform Oracle 9.1 Protocol Analysis
  const performOracleAnalysis = async () => {
    if (!transcript) return
    
    setAnalysisLoading(true)
    try {
      const response = await fetch('/api/oracle/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: transcript,
          participants: participants,
          context: 'Strategic Planning Meeting'
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setAnalysisData(data.analysis)
        addNotification('Analysis Complete', 'Oracle 9.1 Protocol analysis completed successfully', 'success')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      addNotification('Analysis Error', 'Failed to complete Oracle analysis', 'error')
    } finally {
      setAnalysisLoading(false)
    }
  }

  // Add notification
  const addNotification = (title, message, type) => {
    const notification = {
      id: Date.now(),
      title,
      message,
      type,
      timestamp: new Date().toLocaleTimeString()
    }
    setNotifications(prev => [notification, ...prev.slice(0, 4)])
  }

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  // Mock real-time insights
  useEffect(() => {
    if (meetingActive && transcript.length > 50) {
      const insights = [
        'High engagement detected in strategic discussion',
        'Decision point identified - resource allocation',
        'Knowledge sharing opportunity recognized',
        'Collaborative pattern emerging in team dynamics'
      ]
      
      const randomInsight = insights[Math.floor(Math.random() * insights.length)]
      if (!realTimeInsights.includes(randomInsight)) {
        setRealTimeInsights(prev => [...prev, randomInsight])
      }
    }
  }, [transcript, meetingActive])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Oracle Nexus</h1>
                <p className="text-sm text-slate-400">AI Meeting Intelligence</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant={meetingActive ? "default" : "secondary"} className="bg-orange-500/20 text-orange-400">
                {meetingActive ? 'Meeting Active' : 'Standby'}
              </Badge>
              <div className="text-sm text-slate-300">
                {formatTime(meetingDuration)}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Voice Interface */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-800/50 border-slate-700 mb-8">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl">Voice Command Center</CardTitle>
                <CardDescription>
                  Activate voice control for Oracle 9.1 Protocol analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col items-center space-y-6">
                {/* Voice Activation Orb */}
                <motion.div
                  className="relative"
                  animate={isListening ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 2, repeat: isListening ? Infinity : 0 }}
                >
                  <div className={`w-32 h-32 rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 ${
                    isListening 
                      ? 'bg-gradient-to-br from-orange-500 to-red-500 shadow-lg shadow-orange-500/50' 
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                  onClick={toggleListening}
                  >
                    {isListening ? (
                      <Mic className="w-12 h-12 text-white" />
                    ) : (
                      <MicOff className="w-12 h-12 text-slate-300" />
                    )}
                  </div>
                  
                  {isListening && (
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-orange-400"
                      animate={{ scale: [1, 1.5], opacity: [1, 0] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </motion.div>

                {/* Voice Text Display */}
                <div className="w-full max-w-md">
                  <div className="bg-slate-700/50 rounded-lg p-4 min-h-[60px] flex items-center justify-center">
                    <p className="text-center text-slate-300">
                      {voiceText || (isListening ? 'Listening...' : 'Click to activate voice')}
                    </p>
                  </div>
                </div>

                {/* AI Response */}
                <AnimatePresence>
                  {aiResponse && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className="w-full max-w-md"
                    >
                      <Card className="bg-orange-500/10 border-orange-500/30">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-sm text-orange-400">Tanka AI Response</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-slate-300">{aiResponse}</p>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Meeting Controls */}
                <div className="flex space-x-4">
                  <Button
                    onClick={toggleMeeting}
                    className={meetingActive ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'}
                  >
                    {meetingActive ? (
                      <>
                        <Square className="w-4 h-4 mr-2" />
                        End Meeting
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Start Meeting
                      </>
                    )}
                  </Button>
                  
                  <Button
                    onClick={performOracleAnalysis}
                    disabled={!transcript || analysisLoading}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    {analysisLoading ? (
                      <>
                        <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-white border-t-transparent" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Oracle Analysis
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Results */}
            {analysisData && (
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2 text-orange-400" />
                    Oracle 9.1 Protocol Analysis
                  </CardTitle>
                  <CardDescription>
                    Six-dimensional meeting intelligence analysis
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="overview" className="w-full">
                    <TabsList className="grid w-full grid-cols-3 bg-slate-700">
                      <TabsTrigger value="overview">Overview</TabsTrigger>
                      <TabsTrigger value="dimensions">Dimensions</TabsTrigger>
                      <TabsTrigger value="insights">Insights</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="overview" className="mt-6">
                      <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-orange-400">
                            {analysisData.overall_score}/10
                          </div>
                          <div className="text-sm text-slate-400">Overall Score</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-400">
                            {analysisData.participants?.length || 0}
                          </div>
                          <div className="text-sm text-slate-400">Participants</div>
                        </div>
                      </div>
                      
                      <div className="space-y-3">
                        {analysisData.key_insights?.map((insight, index) => (
                          <div key={index} className="flex items-start space-x-3">
                            <Lightbulb className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-slate-300">{insight}</p>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="dimensions" className="mt-6">
                      <div className="space-y-4">
                        {analysisData.analysis && Object.entries(analysisData.analysis).map(([key, data]) => (
                          <div key={key} className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="text-sm font-medium capitalize">
                                {key.replace('_', ' ')}
                              </span>
                              <span className="text-sm text-orange-400">
                                {data.score}/10
                              </span>
                            </div>
                            <Progress value={data.score * 10} className="h-2" />
                            <p className="text-xs text-slate-400">{data.insights}</p>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="insights" className="mt-6">
                      <div className="space-y-4">
                        <h4 className="font-medium text-orange-400">Action Items</h4>
                        {analysisData.action_items?.map((item, index) => (
                          <div key={index} className="flex items-start space-x-3">
                            <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-slate-300">{item}</p>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Participants */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Participants
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {participants.map((participant, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-xs font-medium">
                        {participant.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="text-sm">{participant}</span>
                      <div className="ml-auto">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Real-time Insights */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-yellow-400" />
                  Real-time Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {realTimeInsights.length > 0 ? (
                    realTimeInsights.map((insight, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="flex items-start space-x-3"
                      >
                        <Eye className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-slate-300">{insight}</p>
                      </motion.div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500">Start meeting to see real-time insights</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Notifications */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  Notifications
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {notifications.length > 0 ? (
                    notifications.map((notification) => (
                      <div key={notification.id} className="space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium">{notification.title}</span>
                          <span className="text-xs text-slate-500">{notification.timestamp}</span>
                        </div>
                        <p className="text-xs text-slate-400">{notification.message}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-500">No notifications</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Meeting Transcript */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2" />
                  Live Transcript
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="max-h-40 overflow-y-auto">
                  <p className="text-xs text-slate-300 whitespace-pre-wrap">
                    {transcript || 'Transcript will appear here during meeting...'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

