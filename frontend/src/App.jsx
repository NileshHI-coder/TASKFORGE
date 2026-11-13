import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, Link, useNavigate, useParams } from 'react-router-dom'
import { LayoutDashboard, ListTodo, Search, FileText, Database, GraduationCap, Bot, LogOut, Plus, Activity, ArrowLeft, Sparkles, CheckCircle2, Clock3 } from 'lucide-react'
import { AuthProvider, useAuth } from './context/AuthContext'
import api from './services/api'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line } from 'recharts'

function Shell({ children }) { const { user, logout } = useAuth(); const nav = [{to:'/',label:'Overview',icon:LayoutDashboard},{to:'/tasks',label:'My tasks',icon:ListTodo},{to:'/agents',label:'Agents',icon:Bot},{to:'/research',label:'Research',icon:Search},{to:'/documents',label:'Documents',icon:FileText},{to:'/data',label:'Data analysis',icon:Database},{to:'/exam-solver',label:'Exam solver',icon:GraduationCap}]; return <div className="app-shell"><aside className="sidebar"><Link to="/" className="brand"><span className="brand-mark">T</span><span>TaskForge<small>AI WORKSPACE</small></span></Link><div className="nav-label">WORKSPACE</div>{nav.map(n=><Link className="nav-link" key={n.to} to={n.to}><n.icon size={18}/>{n.label}</Link>)}<div className="sidebar-bottom"><div className="user-chip"><div className="avatar">{user?.name?.[0] || 'U'}</div><div><b>{user?.name || 'Guest'}</b><small>{user?.email || 'Local workspace'}</small></div></div><button className="logout" onClick={logout}><LogOut size={16}/> Sign out</button></div></aside><main className="main-area"><header className="topbar"><div><span className="crumb">Workspace</span><span className="crumb-sep">/</span><b>TaskForge</b></div><div className="top-status"><span className="status-dot"/> Local environment</div></header>{children}</main></div> }
function AuthPage({ mode }) { const { login, register, user } = useAuth(); const [name,setName]=useState(''); const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [error,setError]=useState(''); const [busy,setBusy]=useState(false); const nav=useNavigate(); if(user) return <Navigate to="/"/>; const submit=async e=>{e.preventDefault();setBusy(true);setError('');try{mode==='login'?await login(email,password):await register(name,email,password);nav('/')}catch(err){setError(err.response?.data?.error || 'Could not connect to TaskForge API. Start the Flask backend first.')}finally{setBusy(false)}}; return <div className="auth-wrap"><form className="auth-card" onSubmit={submit}><div className="brand auth-brand"><span className="brand-mark">T</span><span>TaskForge<small>AI WORKSPACE</small></span></div><h1>{mode==='login'?'Welcome back':'Create your workspace'}</h1><p className="muted">{mode==='login'?'Sign in to continue executing your work.':'Start turning complex goals into completed work.'}</p>{mode==='register'&&<label>Full name<input required value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label>}<label>Email address<input type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></label><label>Password<input type="password" required minLength="8" value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 8 characters"/></label>{error&&<div className="error">{error}</div>}<button className="primary full" disabled={busy}>{busy?'Please wait…':mode==='login'?'Sign in':'Create account'}</button><p className="auth-switch">{mode==='login'?<>New to TaskForge? <Link to="/register">Create an account</Link></>:<>Already registered? <Link to="/login">Sign in</Link></>}</p></form></div> }
function Dashboard(){const [tasks,setTasks]=useState([]);const [health,setHealth]=useState('checking');const [title,setTitle]=useState('');const [description,setDescription]=useState('');const [category,setCategory]=useState('general');const [error,setError]=useState('');const load=async()=>{try{const r=await api.get('/tasks');setTasks(r.data.tasks)}catch(e){setError(e.response?.data?.error||'Unable to load tasks. Is the backend running?')}};useEffect(()=>{load();api.get('/health').then(r=>setHealth(r.data.database)).catch(()=>setHealth('offline'))},[]);const create=async e=>{e.preventDefault();setError('');try{await api.post('/tasks',{title,description,category});setTitle('');setDescription('');load()}catch(e){setError(e.response?.data?.error||'Could not create task')}};const completed=tasks.filter(t=>t.status==='completed').length;return <div className="page"><div className="page-heading"><div><div className="eyebrow">YOUR COMMAND CENTRE</div><h1>Good work starts here.</h1><p className="muted">Turn your goals into structured, verifiable outcomes.</p></div><div className="connection-pill"><span className={health==='connected'?'status-dot':'status-dot warn'}/>{health==='connected'?'MySQL connected':`Database ${health}`}</div></div><div className="stats-grid"><Stat label="Total tasks" value={tasks.length} icon={ListTodo}/><Stat label="Completed" value={completed} icon={Activity}/><Stat label="In progress" value={tasks.filter(t=>['running','planning','verification'].includes(t.status)).length} icon={Bot}/><Stat label="Needs attention" value={tasks.filter(t=>t.status==='failed').length} icon={Activity}/></div><div className="content-grid"><section className="panel composer"><div className="panel-head"><div><h2>Create a task</h2><p className="muted">Describe the outcome you want TaskForge to deliver.</p></div><span className="soft-icon"><Plus size={18}/></span></div><form onSubmit={create}><label>Task title<input required maxLength="255" value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Research renewable energy trends"/></label><label>What do you want to accomplish?<textarea rows="4" value={description} onChange={e=>setDescription(e.target.value)} placeholder="Add context, requirements, and expected output…"/></label><label>Workflow<select value={category} onChange={e=>setCategory(e.target.value)}><option value="general">Automatic / General</option><option value="research">Research & analysis</option><option value="document">Document creation</option><option value="planning">Project planning</option><option value="data_analysis">Data analysis</option><option value="exam_solver">Exam solver</option></select></label>{error&&<div className="error">{error}</div>}<button className="primary"><Plus size={16}/> Create task</button></form></section><section className="panel tasks-panel"><div className="panel-head"><div><h2>Recent tasks</h2><p className="muted">Your latest work and execution status.</p></div><Link className="text-link" to="/tasks">View all</Link></div>{tasks.length===0?<div className="empty"><div className="empty-icon"><ListTodo/></div><b>No tasks yet</b><p className="muted">Create your first task to get started.</p></div>:<div className="task-list">{tasks.slice(0,6).map(t=><Link to={`/tasks/${t.id}`} className="task-row task-row-link" key={t.id}><div className="task-symbol"><FileText size={17}/></div><div className="task-info"><b>{t.title}</b><small>{t.category.replace('_',' ')} · {new Date(t.created_at).toLocaleDateString()}</small></div><span className={`badge ${t.status}`}>{t.status}</span></Link>)}</div>}</section></div><div className="notice"><Bot size={18}/><div><b>Planner Agent is now available</b><p>Open a task to generate a structured plan, review specialist assignments, and approve the subtasks. Actual agent execution is the next milestone.</p></div></div></div>}
function Stat({label,value,icon:Icon}){return <div className="stat-card"><div className="stat-top"><span>{label}</span><Icon size={17}/></div><strong>{value}</strong></div>}
function Tasks(){const [tasks,setTasks]=useState([]);const [err,setErr]=useState('');useEffect(()=>{api.get('/tasks').then(r=>setTasks(r.data.tasks)).catch(e=>setErr(e.response?.data?.error||'Unable to load tasks'))},[]);return <div className="page"><div className="page-heading"><div><div className="eyebrow">WORKSPACE</div><h1>My tasks</h1><p className="muted">Review the tasks you have created.</p></div><Link to="/" className="primary link-button"><Plus size={16}/> New task</Link></div>{err&&<div className="error">{err}</div>}<div className="panel">{tasks.length===0?<div className="empty"><b>No tasks found</b><p className="muted">Your created tasks will appear here.</p></div>:tasks.map(t=><Link to={`/tasks/${t.id}`} className="task-row task-row-link" key={t.id}><div className="task-symbol"><FileText size={17}/></div><div className="task-info"><b>{t.title}</b><small>{t.description||'No additional description'} · {new Date(t.created_at).toLocaleString()}</small></div><span className={`badge ${t.status}`}>{t.status}</span></Link>)}</div></div>}

function TaskDetail(){
 const {taskId}=useParams(); const [task,setTask]=useState(null); const [summary,setSummary]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState(''); const [message,setMessage]=useState(''); const [executions,setExecutions]=useState([]); const [activity,setActivity]=useState([]);
 const load=async()=>{try{const r=await api.get(`/tasks/${taskId}`);setTask(r.data.task);setSummary(r.data.task.plan_summary||'');try{const x=await api.get(`/tasks/${taskId}/executions`);setExecutions(x.data.executions||[]);setActivity(x.data.activity||[])}catch{}}catch(e){setError(e.response?.data?.error||'Unable to load this task')}};
 useEffect(()=>{load()},[taskId]);
 const generate=async()=>{setBusy(true);setError('');setMessage('');try{const r=await api.post(`/tasks/${taskId}/plan`);setTask(r.data.task);setSummary(r.data.plan_summary||'')}catch(e){setError(e.response?.data?.error||'Planner request failed')}finally{setBusy(false)}};
 const executeNext=async()=>{setBusy(true);setError('');setMessage('');try{const r=await api.post(`/tasks/${taskId}/execute-next`);setTask(r.data.task);setMessage(r.data.message);const x=await api.get(`/tasks/${taskId}/executions`);setExecutions(x.data.executions||[]);setActivity(x.data.activity||[])}catch(e){setError(e.response?.data?.error||'Agent execution failed');if(e.response?.data?.task)setTask(e.response.data.task)}finally{setBusy(false)}};
 const verify=async()=>{setBusy(true);setError('');setMessage('');try{const r=await api.post(`/tasks/${taskId}/verify`);setTask(r.data.task);setMessage('Verification review completed. Read the verifier output below.')}catch(e){setError(e.response?.data?.error||'Verification failed')}finally{setBusy(false)}};
 const retry=async(id)=>{setBusy(true);setError('');try{const r=await api.post(`/tasks/${taskId}/subtasks/${id}/retry`);setTask(r.data.task);setMessage(r.data.message)}catch(e){setError(e.response?.data?.error||'Retry could not be queued')}finally{setBusy(false)}};
 const approve=async()=>{setBusy(true);setError('');setMessage('');try{const r=await api.post(`/tasks/${taskId}/approve-plan`);setTask(r.data.task);setMessage(r.data.message)}catch(e){setError(e.response?.data?.error||'Could not approve plan')}finally{setBusy(false)}};
 if(!task&&!error)return <div className="page"><p className="muted">Loading task…</p></div>;
 if(!task)return <div className="page"><div className="error">{error}</div><Link to="/tasks" className="text-link">Back to tasks</Link></div>;
 return <div className="page"><Link to="/tasks" className="back-link"><ArrowLeft size={16}/> Back to tasks</Link><div className="page-heading task-detail-heading"><div><div className="eyebrow">TASK WORKSPACE · #{task.id}</div><h1>{task.title}</h1><p className="muted">{task.description||'No additional task context provided.'}</p></div><span className={`badge ${task.status}`}>{task.status}</span></div>
 <div className="panel plan-panel"><div className="panel-head"><div><h2>Execution plan</h2><p className="muted">The Planner Agent turns this goal into reviewable specialist-agent steps.</p></div><span className="soft-icon"><Sparkles size={18}/></span></div>
 {summary&&<div className="plan-summary"><b>Planner summary</b><p>{summary}</p></div>}
 {task.subtasks?.length? <div className="subtask-list">{task.subtasks.map((s,i)=><div className="subtask-card" key={s.id}><div className="subtask-number">{String(i+1).padStart(2,'0')}</div><div className="subtask-content"><div className="subtask-title-row"><b>{s.title}</b><span className={`badge ${s.status}`}>{s.status.replaceAll('_',' ')}</span></div><p>{s.description}</p><div className="subtask-meta"><span><Bot size={14}/> {s.agent_type.replaceAll('_',' ')}</span>{s.expected_output&&<span><CheckCircle2 size={14}/> {s.expected_output}</span>}</div>{s.dependencies?.length>0&&<small className="dependency-note">Depends on: {s.dependencies.join(', ')}</small>}</div></div>)}</div>:<div className="empty"><div className="empty-icon"><Sparkles/></div><b>No plan generated yet</b><p className="muted">Generate a plan to see the subtasks and the agents assigned to them.</p></div>}
 {error&&<div className="error">{error}</div>}{message&&<div className="success-message">{message}</div>}
 <div className="plan-actions">{!task.plan_approved&&<button className="secondary" onClick={generate} disabled={busy}><Sparkles size={16}/>{busy?'Working…':task.subtasks?.length?'Regenerate plan':'Generate plan'}</button>}{task.subtasks?.length>0&&!task.plan_approved&&<button className="primary" onClick={approve} disabled={busy}><CheckCircle2 size={16}/> Approve plan</button>}{task.plan_approved&&<><div className="approved-note"><CheckCircle2 size={17}/> Plan approved · execution enabled</div>{task.subtasks?.some(s=>s.status==='queued')&&<button className="primary" onClick={executeNext} disabled={busy}><Bot size={16}/>{busy?'Agent working…':'Execute next subtask'}</button>}{task.subtasks?.some(s=>s.status==='failed')&&task.subtasks.filter(s=>s.status==='failed').map(s=><button className="secondary" key={s.id} onClick={()=>retry(s.id)} disabled={busy}>Retry: {s.title}</button>)}{task.subtasks?.length>0&&task.subtasks.every(s=>s.status==='completed')&&<button className="primary" onClick={verify} disabled={busy}><CheckCircle2 size={16}/>{busy?'Verifying…':'Run independent verification'}</button>}</>}</div>
 </div>{executions.length>0&&<section className="panel execution-panel"><div className="panel-head"><div><h2>Agent execution history</h2><p className="muted">Recorded runs and their outcomes.</p></div><Activity size={18}/></div>{executions.map(x=><div className="task-row" key={x.id}><div className="task-info"><b>{x.agent_name.replaceAll('_',' ')} agent</b><small>{x.input_summary}</small>{x.error_summary&&<small className="error">{x.error_summary}</small>}</div><span className={`badge ${x.status}`}>{x.status}</span></div>)}</section>}{task.result&&<section className="panel"><h2>Verification report / task result</h2><pre className="result-output">{task.result}</pre></section>}{activity.length>0&&<section className="panel"><h2>Activity timeline</h2>{activity.map((a,i)=><div className="activity-line" key={i}><span className="status-dot"/><div><b>{a.message}</b><small>{new Date(a.created_at).toLocaleString()}</small></div></div>)}</section>}<div className="notice"><Clock3 size={18}/><div><b>Execution model</b><p>Run one approved subtask at a time. This keeps progress visible and lets you retry failed steps. Long-running background workers and live push updates remain future improvements.</p></div></div></div>
}

function ResearchStudio(){
 const [tasks,setTasks]=useState([]);const [taskId,setTaskId]=useState('');const [query,setQuery]=useState('');const [depth,setDepth]=useState('advanced');const [topic,setTopic]=useState('general');const [report,setReport]=useState('');const [sources,setSources]=useState([]);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [message,setMessage]=useState('');
 useEffect(()=>{api.get('/tasks').then(r=>{const ts=r.data.tasks||[];setTasks(ts);const preferred=ts.find(t=>t.category==='research');if(preferred)setTaskId(String(preferred.id))}).catch(()=>setError('Could not load tasks'))},[]);
 const run=async e=>{e.preventDefault();setBusy(true);setError('');setMessage('');setReport('');setSources([]);try{let id=taskId;if(!id){const c=await api.post('/tasks',{title:query.slice(0,180),description:query,category:'research'});id=String(c.data.task.id);setTaskId(id);setTasks(v=>[c.data.task,...v])}const r=await api.post(`/research/${id}/run`,{query,search_depth:depth,topic,max_results:6});setReport(r.data.report);setSources(r.data.sources||[]);setMessage(`Research completed using ${r.data.sources?.length||0} source(s).`)}catch(err){setError(err.response?.data?.error||'Research could not be completed.')}finally{setBusy(false)}};
 const exportReport=async format=>{try{const r=await api.post(`/research/${taskId}/export`,{format});const f=await api.get(r.data.download_url,{responseType:'blob'});const url=URL.createObjectURL(f.data);const a=document.createElement('a');a.href=url;a.download=r.data.file.filename;a.click();URL.revokeObjectURL(url)}catch(e){setError(e.response?.data?.error||'Export failed')}};
 return <div className="page"><div className="page-heading"><div><div className="eyebrow">TAVILY + GEMINI</div><h1>Research workspace</h1><p className="muted">Search current web evidence, synthesize findings, and export a sourced report.</p></div></div><form className="panel studio-form" onSubmit={run}><label>Research question<textarea required rows="4" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Example: Compare current approaches to AI-powered crop price forecasting, including benefits and limitations."/></label><div className="form-grid"><label>Existing task (optional)<select value={taskId} onChange={e=>setTaskId(e.target.value)}><option value="">Create a new research task</option>{tasks.map(t=><option key={t.id} value={t.id}>{t.title}</option>)}</select></label><label>Search depth<select value={depth} onChange={e=>setDepth(e.target.value)}><option value="basic">Basic</option><option value="advanced">Advanced</option></select></label><label>Research topic<select value={topic} onChange={e=>setTopic(e.target.value)}><option value="general">General</option><option value="news">News</option><option value="finance">Finance</option></select></label></div>{error&&<div className="error">{error}</div>}{message&&<div className="success-message">{message}</div>}<button className="primary" disabled={busy||!query.trim()}><Search size={16}/>{busy?'Searching and synthesizing…':'Run web research'}</button></form>
 {report&&<><section className="panel report-panel"><div className="panel-head"><div><h2>Research report</h2><p className="muted">Claims are cited against retrieved source numbers. Review original sources before relying on important claims.</p></div><div className="export-actions"><button className="secondary" onClick={()=>exportReport('pdf')}>Export PDF</button><button className="secondary" onClick={()=>exportReport('docx')}>Export DOCX</button></div></div><pre className="result-output">{report}</pre></section><section className="panel"><h2>Retrieved sources ({sources.length})</h2>{sources.map((s,i)=><div className="source-row" key={s.url}><b>[{i+1}] {s.title}</b><small>{s.published_date||'Publication date not supplied'}{s.score!=null?` · relevance ${Number(s.score).toFixed(2)}`:''}</small><p>{s.content}</p><a href={s.url} target="_blank" rel="noreferrer">Open original source</a></div>)}</section></>}
 <div className="notice"><Search size={18}/><div><b>Evidence policy</b><p>TaskForge uses Tavily results as evidence and Gemini to synthesize them. If an API is not configured or a source does not provide a publication date, the interface reports that limitation rather than fabricating it.</p></div></div></div>
}
function DocumentStudio(){
 const [tasks,setTasks]=useState([]);const [taskId,setTaskId]=useState('');const [title,setTitle]=useState('');const [instructions,setInstructions]=useState('');const [content,setContent]=useState('');const [format,setFormat]=useState('docx');const [files,setFiles]=useState([]);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [message,setMessage]=useState('');
 const loadFiles=()=>api.get('/documents/files').then(r=>setFiles(r.data.files||[])).catch(()=>{});useEffect(()=>{api.get('/tasks').then(r=>{const ts=r.data.tasks||[];setTasks(ts);if(ts[0]){setTaskId(String(ts[0].id));setTitle(ts[0].title);setContent(ts[0].result||ts[0].description||'')}}).catch(()=>setError('Could not load tasks'));loadFiles()},[]);
 const choose=id=>{setTaskId(id);const t=tasks.find(x=>String(x.id)===id);if(t){setTitle(t.title);setContent(t.result||t.description||'')}};
 const generate=async e=>{e.preventDefault();setBusy(true);setError('');setMessage('');try{const r=await api.post('/documents/generate',{task_id:Number(taskId),title,instructions,content,format});setMessage(`Created ${r.data.file.filename}`);const f=await api.get(r.data.download_url,{responseType:'blob'});const url=URL.createObjectURL(f.data);const a=document.createElement('a');a.href=url;a.download=r.data.file.filename;a.click();URL.revokeObjectURL(url);loadFiles()}catch(err){setError(err.response?.data?.error||'Document generation failed')}finally{setBusy(false)}};
 const download=async f=>{try{const r=await api.get(`/documents/files/${f.id}/download`,{responseType:'blob'});const url=URL.createObjectURL(r.data);const a=document.createElement('a');a.href=url;a.download=f.filename;a.click();URL.revokeObjectURL(url)}catch(e){setError('Could not download this file')}};
 return <div className="page"><div className="page-heading"><div><div className="eyebrow">GEMINI DOCUMENT GENERATION</div><h1>Document studio</h1><p className="muted">Turn task context or your own content into downloadable professional documents.</p></div></div><form className="panel studio-form" onSubmit={generate}><div className="form-grid"><label>Source task<select required value={taskId} onChange={e=>choose(e.target.value)}><option value="">Select a task</option>{tasks.map(t=><option key={t.id} value={t.id}>{t.title}</option>)}</select></label><label>Document title<input required value={title} onChange={e=>setTitle(e.target.value)} placeholder="Document title"/></label><label>Output format<select value={format} onChange={e=>setFormat(e.target.value)}><option value="docx">Word document (.docx)</option><option value="pdf">PDF (.pdf)</option></select></label></div><label>Instructions<textarea rows="3" value={instructions} onChange={e=>setInstructions(e.target.value)} placeholder="Example: Organize this into an executive summary, key findings, recommendations, and conclusion."/></label><label>Source content<textarea rows="9" value={content} onChange={e=>setContent(e.target.value)} placeholder="Paste content or select a task with an existing result."/></label>{error&&<div className="error">{error}</div>}{message&&<div className="success-message">{message}</div>}<button className="primary" disabled={busy||!taskId||(!content.trim()&&!instructions.trim())}><FileText size={16}/>{busy?'Generating document…':'Generate and download'}</button></form><section className="panel files-panel"><div className="panel-head"><div><h2>Generated files</h2><p className="muted">Files created in this workspace.</p></div></div>{files.length===0?<p className="muted">No generated files yet.</p>:files.map(f=><div className="task-row" key={f.id}><div className="task-symbol"><FileText size={17}/></div><div className="task-info"><b>{f.filename}</b><small>{new Date(f.created_at).toLocaleString()}</small></div><button className="secondary" onClick={()=>download(f)}>Download</button></div>)}</section></div>
}


function DataAnalysisStudio(){
 const [file,setFile]=useState(null),[analysis,setAnalysis]=useState(null),[runs,setRuns]=useState([]),[busy,setBusy]=useState(false),[error,setError]=useState(''),[message,setMessage]=useState('');
 const loadRuns=async()=>{try{const r=await api.get('/data/runs');setRuns(r.data.runs||[])}catch{}};
 useEffect(()=>{loadRuns()},[]);
 const upload=async e=>{e.preventDefault();if(!file)return;setBusy(true);setError('');setMessage('');const body=new FormData();body.append('file',file);try{const r=await api.post('/data/upload',body,{headers:{'Content-Type':'multipart/form-data'}});setAnalysis(r.data.analysis);setMessage('Dataset analysed and saved to your workspace.');loadRuns()}catch(err){setError(err.response?.data?.error||'Upload or analysis failed.')}finally{setBusy(false)}};
 const openRun=async id=>{setBusy(true);setError('');try{const r=await api.get(`/data/runs/${id}`);setAnalysis(r.data.analysis)}catch(err){setError(err.response?.data?.error||'Could not load analysis')}finally{setBusy(false)}};
 const insights=async()=>{if(!analysis)return;setBusy(true);setError('');try{const r=await api.post(`/data/runs/${analysis.id}/insights`);setAnalysis({...analysis,ai_insights:r.data.ai_insights})}catch(err){setError(err.response?.data?.error||'AI analysis failed')}finally{setBusy(false)}};
 const result=analysis?.result||{},numeric=result.numeric_summary||{},chartData=Object.entries(numeric).map(([name,v])=>({name,mean:v.mean,median:v.median}));
 return <div className="page"><div className="page-heading"><div><div className="eyebrow">TASKFORGE WORKSPACE · MILESTONE 5</div><h1>Data Analysis Studio</h1><p className="muted">Upload a dataset, inspect its quality, and turn raw rows into evidence-backed insights.</p></div><div className="connection-pill"><span className="status-dot"/> CSV · Excel</div></div>
 <section className="panel data-upload-panel"><div className="panel-head"><div><h2>Import dataset</h2><p className="muted">Supported formats: CSV, XLSX and XLS · Maximum 10 MB</p></div><span className="soft-icon"><Database size={18}/></span></div><form className="studio-form" onSubmit={upload}><label>Choose dataset<input type="file" accept=".csv,.xlsx,.xls" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><div className="export-actions"><button className="primary" disabled={!file||busy}>{busy?'Processing…':'Upload & analyse'}</button>{file&&<span className="muted">{file.name}</span>}</div></form>{error&&<div className="error">{error}</div>}{message&&<div className="approved-note">{message}</div>}</section>
 <div className="data-layout"><section className="panel"><div className="panel-head"><div><h2>Analysis history</h2><p className="muted">Your latest uploaded datasets.</p></div></div>{runs.length===0?<div className="empty"><b>No datasets yet</b><p className="muted">Upload a CSV or Excel workbook to begin.</p></div>:runs.map(r=><button className={`data-run ${analysis?.id===r.id?'selected':''}`} key={r.id} onClick={()=>openRun(r.id)}><b>{r.filename}</b><small>{r.row_count.toLocaleString()} rows · {r.column_count} columns · {new Date(r.created_at).toLocaleDateString()}</small></button>)}</section>
 {analysis&&<div className="data-results"><div className="stats-grid data-stats"><Stat label="Rows" value={result.shape?.rows??0} icon={ListTodo}/><Stat label="Columns" value={result.shape?.columns??0} icon={Database}/><Stat label="Missing cells" value={result.total_missing??0} icon={Activity}/><Stat label="Duplicate rows" value={result.duplicate_rows??0} icon={CheckCircle2}/></div>
 <section className="panel"><div className="panel-head"><div><h2>Column profile</h2><p className="muted">Detected types, missing cells and unique values.</p></div></div><div className="table-scroll"><table className="data-table"><thead><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique</th></tr></thead><tbody>{(result.columns||[]).map(c=><tr key={c.name}><td>{c.name}</td><td>{c.dtype}</td><td>{c.missing}</td><td>{c.unique}</td></tr>)}</tbody></table></div></section>
 <section className="panel"><div className="panel-head"><div><h2>Numeric summary</h2><p className="muted">Mean and median for numeric columns.</p></div></div>{chartData.length?<><div className="chart-wrap"><ResponsiveContainer width="100%" height={260}><BarChart data={chartData}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="mean" name="Mean" fill="#5865d9"/><Bar dataKey="median" name="Median" fill="#22a06b"/></BarChart></ResponsiveContainer></div><div className="table-scroll"><table className="data-table"><thead><tr><th>Column</th><th>Mean</th><th>Median</th><th>Std dev</th><th>Min</th><th>Max</th></tr></thead><tbody>{Object.entries(numeric).map(([k,v])=><tr key={k}><td>{k}</td><td>{v.mean}</td><td>{v.median}</td><td>{v.std}</td><td>{v.min}</td><td>{v.max}</td></tr>)}</tbody></table></div></>:<p className="muted">No numeric columns were detected in this dataset.</p>}</section>
 <section className="panel"><div className="panel-head"><div><h2>Distribution explorer</h2><p className="muted">Numeric histograms and categorical frequency charts.</p></div></div>{Object.entries(result.histograms||{}).map(([column,bins])=><div className="mini-chart" key={column}><b>{column} · histogram</b><div className="chart-wrap"><ResponsiveContainer width="100%" height={220}><BarChart data={bins}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="range"/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="count" fill="#5865d9"/></BarChart></ResponsiveContainer></div></div>)}{Object.entries(result.categorical_distributions||{}).map(([column,items])=><div className="mini-chart" key={column}><b>{column} · category counts</b><div className="chart-wrap"><ResponsiveContainer width="100%" height={220}><BarChart data={items}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="label"/><YAxis allowDecimals={false}/><Tooltip/><Bar dataKey="value" fill="#22a06b"/></BarChart></ResponsiveContainer></div></div>)}</section>
 <section className="panel"><div className="panel-head"><div><h2>Numeric trends</h2><p className="muted">First 50 non-missing values in file order; not a time-series forecast.</p></div></div>{Object.entries(result.numeric_series||{}).map(([column,values])=><div className="mini-chart" key={column}><b>{column}</b><div className="chart-wrap"><ResponsiveContainer width="100%" height={200}><LineChart data={values.map((value,index)=>({row:index+1,value}))}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="row"/><YAxis/><Tooltip/><Line type="monotone" dataKey="value" stroke="#5865d9" dot={false}/></LineChart></ResponsiveContainer></div></div>)}</section>
 <section className="panel"><div className="panel-head"><div><h2>Correlation checks</h2><p className="muted">Pairwise Pearson correlation for numeric columns; correlation does not imply causation.</p></div></div>{result.correlations?.length?<><div className="heatmap-grid">{result.correlations.map(c=><div className="heatmap-cell" key={c.x+c.y} style={{backgroundColor:`rgba(88,101,217,${Math.max(.12,Math.abs(c.value))})`}}><b>{c.value}</b><small>{c.x} × {c.y}</small></div>)}</div>{result.correlations.map(c=><div className="correlation-row" key={c.x+c.y}><span>{c.x} ↔ {c.y}</span><b>{c.value}</b></div>)}</>:<p className="muted">At least two numeric columns are needed for correlation analysis.</p>}</section>
 <section className="panel"><div className="panel-head"><div><h2>Data preview</h2><p className="muted">First 10 rows of the uploaded dataset.</p></div></div><div className="table-scroll"><table className="data-table"><thead><tr>{(result.preview?.columns||[]).map(c=><th key={c}>{c}</th>)}</tr></thead><tbody>{(result.preview?.rows||[]).map((row,i)=><tr key={i}>{row.map((v,j)=><td key={j}>{v===null?'—':String(v)}</td>)}</tr>)}</tbody></table></div></section>
 <section className="panel"><div className="panel-head"><div><h2>AI analyst</h2><p className="muted">Gemini explains patterns from computed statistics, with limitations.</p></div><button className="primary" onClick={insights} disabled={busy}>{busy?'Working…':'Generate insights'}</button></div>{analysis.ai_insights?<div className="result-output">{analysis.ai_insights}</div>:<p className="muted">Generate an AI interpretation after reviewing the statistical results.</p>}</section></div>}
 </div></div>
}


function ExamSolverStudio(){
 const [file,setFile]=useState(null),[exam,setExam]=useState(null),[runs,setRuns]=useState([]),[busy,setBusy]=useState(false),[error,setError]=useState(''),[message,setMessage]=useState('');
 const load=async()=>{try{const r=await api.get('/exams/runs');setRuns(r.data.exams||[])}catch{}};
 useEffect(()=>{load()},[]);
 const upload=async e=>{e.preventDefault();if(!file)return;setBusy(true);setError('');setMessage('');const body=new FormData();body.append('file',file);try{const r=await api.post('/exams/upload',body,{headers:{'Content-Type':'multipart/form-data'}});setExam(r.data.exam);setMessage('Document extracted. Review the detected questions before solving.');load()}catch(err){setError(err.response?.data?.error||'Document extraction failed.')}finally{setBusy(false)}};
 const open=async id=>{setBusy(true);setError('');try{const r=await api.get(`/exams/runs/${id}`);setExam(r.data.exam)}catch(err){setError(err.response?.data?.error||'Could not load exam')}finally{setBusy(false)}};
 const solve=async()=>{if(!exam)return;setBusy(true);setError('');try{const r=await api.post(`/exams/runs/${exam.id}/solve`);setExam(r.data.exam);setMessage('Solutions generated and independently reviewed by a second AI pass.')}catch(err){setError(err.response?.data?.error||'Solving failed.')}finally{setBusy(false)}};
 const download=async format=>{try{const r=await api.get(`/exams/runs/${exam.id}/download?format=${format}`,{responseType:'blob'});const url=URL.createObjectURL(r.data);const a=document.createElement('a');a.href=url;a.download=`TaskForge-Solution-${exam.id}.${format}`;a.click();URL.revokeObjectURL(url)}catch(err){setError('Could not export solution. Solve the paper first.')}};
 const result=exam?.result||{};
 return <div className="page"><div className="page-heading"><div><div className="eyebrow">TASKFORGE WORKSPACE · MILESTONE 6</div><h1>Exam Solver</h1><p className="muted">Extract questions from papers, generate worked solutions, and run a separate verification pass.</p></div><div className="connection-pill"><span className="status-dot"/> PDF · OCR · Gemini</div></div>
 <section className="panel data-upload-panel"><div className="panel-head"><div><h2>Upload question paper</h2><p className="muted">PDF, PNG, JPG, TIFF or WEBP · Up to 15 MB · PDF maximum 40 pages</p></div><span className="soft-icon"><GraduationCap size={18}/></span></div><form className="studio-form" onSubmit={upload}><label>Select paper or scanned image<input type="file" accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff,.webp,application/pdf,image/*" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><div className="export-actions"><button className="primary" disabled={!file||busy}>{busy?'Processing…':'Upload & extract questions'}</button>{file&&<span className="muted">{file.name}</span>}</div></form>{error&&<div className="error">{error}</div>}{message&&<div className="approved-note">{message}</div>}</section>
 <div className="data-layout"><section className="panel"><div className="panel-head"><div><h2>Paper history</h2><p className="muted">Your recent uploads.</p></div></div>{runs.length===0?<div className="empty"><b>No papers uploaded</b><p className="muted">Upload a previous-year paper or practice sheet.</p></div>:runs.map(r=><button className={`data-run ${exam?.id===r.id?'selected':''}`} key={r.id} onClick={()=>open(r.id)}><b>{r.filename}</b><small>{r.result?.question_count||0} questions · {r.status} · {new Date(r.created_at).toLocaleDateString()}</small></button>)}</section>
 {exam&&<div className="data-results"><section className="panel"><div className="panel-head"><div><h2>Extraction review</h2><p className="muted">{result.question_count||0} detected questions · {result.extraction_characters||0} extracted characters</p></div><span className={`badge ${exam.status==='solved'?'completed':'planning'}`}>{exam.status}</span></div><div className="notice"><div><b>Review OCR before relying on answers</b><p>{result.extraction_note} Mathematical symbols, tables and diagrams may be misread or omitted.</p></div></div>{(result.questions||[]).map((q,i)=><article className="exam-question" key={`${q.number}-${i}`}><div className="exam-question-head"><b>Question {q.number}</b><span className="badge">{q.type}</span></div><p>{q.text}</p></article>)}<button className="primary" disabled={busy||!result.questions?.length} onClick={solve}>{busy?'Solving & verifying…':result.answers?'Regenerate solutions':'Solve & independently verify'}</button></section>
 {result.answers?.length>0&&<section className="panel"><div className="panel-head"><div><h2>Worked solutions</h2><p className="muted">AI-generated answers with a separate verification review.</p></div><div className="export-actions"><button className="secondary" onClick={()=>download('pdf')}>PDF</button><button className="secondary" onClick={()=>download('docx')}>DOCX</button></div></div>{result.answers.map((a,i)=><article className="exam-answer" key={`${a.number}-${i}`}><div className="exam-question-head"><b>Question {a.number}</b><span className={`badge ${a.verification?.status==='VERIFIED'?'completed':a.verification?.status==='INCORRECT'?'failed':'planning'}`}>{a.verification?.status||'NEEDS_REVIEW'}</span></div><div className="result-output">{a.answer}</div><p className="muted">Confidence: {a.confidence||'LOW'} · Review: {a.verification?.feedback||'No independent review returned.'}</p></article>)}<div className="notice"><div><b>Important accuracy note</b><p>{result.verification_note} AI verification is not a guarantee of correctness, especially for OCR, complex diagrams and numerical work.</p></div></div></section>}
 </div>}
 </div></div>
}

function AgentActivity() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  const agentTypes = [
    { id: 'planner', name: 'Planner Agent', description: 'Breaks tasks into structured subtasks.' },
    { id: 'research', name: 'Research Agent', description: 'Researches information and evidence.' },
    { id: 'document', name: 'Document Agent', description: 'Creates structured documents.' },
    { id: 'data_analysis', name: 'Data Analysis Agent', description: 'Analyses datasets and insights.' },
    { id: 'project_planning', name: 'Project Planning Agent', description: 'Builds project plans and timelines.' },
    { id: 'exam_solver', name: 'Exam Solver Agent', description: 'Processes and solves exam questions.' },
    { id: 'verification', name: 'Verification Agent', description: 'Reviews completed outputs.' }
  ];

  const loadActivity = async () => {
    setLoading(true);
    setError('');

    try {
      const taskResponse = await api.get('/tasks');
      const tasks = taskResponse.data.tasks || [];

      const detailedTasks = await Promise.all(
        tasks.map(async (task) => {
          try {
            const [detailResponse, executionResponse] = await Promise.all([
              api.get(`/tasks/${task.id}`),
              api.get(`/tasks/${task.id}/executions`)
            ]);

            return {
              ...detailResponse.data.task,
              executions: executionResponse.data.executions || [],
              activity: executionResponse.data.activity || []
            };
          } catch {
            return {
              ...task,
              subtasks: [],
              executions: [],
              activity: []
            };
          }
        })
      );

      setRecords(detailedTasks);
      setLastUpdated(new Date());
    } catch (err) {
      setError(
        err.response?.data?.error ||
        'Unable to load agent activity. Check that Flask and MySQL are running.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActivity();
  }, []);

  const allSubtasks = records.flatMap(task =>
    (task.subtasks || []).map(subtask => ({
      ...subtask,
      taskId: task.id,
      taskTitle: task.title
    }))
  );

  const allExecutions = records.flatMap(task =>
    (task.executions || []).map(execution => ({
      ...execution,
      taskId: task.id,
      taskTitle: task.title
    }))
  );

  const allActivity = records
    .flatMap(task =>
      (task.activity || []).map(item => ({
        ...item,
        taskId: task.id,
        taskTitle: task.title
      }))
    )
    .sort((a, b) =>
      new Date(b.created_at || 0) - new Date(a.created_at || 0)
    );

  const getAgentStatus = (agentId) => {
    if (agentId === 'planner') {
      const planned = records.some(task => (task.subtasks || []).length > 0);
      return planned ? 'completed' : 'idle';
    }

    const executions = allExecutions.filter(
      item => item.agent_name === agentId
    );

    const subtasks = allSubtasks.filter(
      item => item.agent_type === agentId
    );

    if (executions.some(item => item.status === 'running') ||
        subtasks.some(item => item.status === 'running')) return 'running';

    if (executions.some(item => item.status === 'failed') ||
        subtasks.some(item => item.status === 'failed')) return 'failed';

    if (executions.some(item => item.status === 'completed') ||
        subtasks.some(item => item.status === 'completed')) return 'completed';

    if (subtasks.some(item =>
      ['queued', 'waiting_for_approval'].includes(item.status)
    )) return 'queued';

    return 'idle';
  };

  const countStatus = status =>
    allSubtasks.filter(item => item.status === status).length;

  const statusClass = status => {
    if (status === 'completed') return 'completed';
    if (status === 'failed') return 'failed';
    if (status === 'running') return 'running';
    return '';
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">MULTI-AGENT MONITORING</div>
          <h1>Agent Activity</h1>
          <p className="muted">
            Monitor specialist assignments, execution history and workflow progress.
          </p>
        </div>
        <button className="secondary" onClick={loadActivity} disabled={loading}>
          <Activity size={16}/>
          {loading ? 'Refreshing…' : 'Refresh activity'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="stats-grid">
        <Stat label="Total executions" value={allExecutions.length} icon={Bot}/>
        <Stat label="Completed subtasks" value={countStatus('completed')} icon={CheckCircle2}/>
        <Stat label="Running subtasks" value={countStatus('running')} icon={Activity}/>
        <Stat label="Failed subtasks" value={countStatus('failed')} icon={Clock3}/>
      </div>

      <section className="panel" style={{ marginBottom: 18 }}>
        <div className="panel-head">
          <div>
            <h2>Specialized agents</h2>
            <p className="muted">
              Status is calculated from your saved plans and execution records.
            </p>
          </div>
          <Bot size={20}/>
        </div>

        <div className="agent-grid">
          {agentTypes.map(agent => {
            const status = getAgentStatus(agent.id);
            const assigned = allSubtasks.filter(
              item => item.agent_type === agent.id
            ).length;
            const runs = allExecutions.filter(
              item => item.agent_name === agent.id
            ).length;

            return (
              <div className="agent-card" key={agent.id}>
                <div className="agent-card-top">
                  <div className="soft-icon"><Bot size={19}/></div>
                  <span className={`badge ${statusClass(status)}`}>
                    {status.replaceAll('_', ' ')}
                  </span>
                </div>
                <h3>{agent.name}</h3>
                <p className="muted">{agent.description}</p>
                <div className="agent-meta">
                  <span>{assigned} assigned</span>
                  <span>{runs} executions</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="panel execution-panel">
        <div className="panel-head">
          <div>
            <h2>Execution traces</h2>
            <p className="muted">
              Actual recorded agent runs from your tasks.
            </p>
          </div>
          <Activity size={18}/>
        </div>

        {loading ? (
          <div className="empty">Loading execution records…</div>
        ) : allExecutions.length === 0 ? (
          <div className="empty">
            <div className="empty-icon"><Bot/></div>
            <b>No agent executions yet</b>
            <p className="muted">
              Create a task, generate its plan, approve it and execute a subtask.
              Its real execution trace will appear here.
            </p>
          </div>
        ) : (
          allExecutions
            .slice()
            .sort((a, b) =>
              new Date(b.started_at || 0) - new Date(a.started_at || 0)
            )
            .map(item => (
              <div className="task-row" key={item.id}>
                <div className="task-symbol"><Bot size={17}/></div>
                <div className="task-info">
                  <b>{item.agent_name.replaceAll('_', ' ')} Agent</b>
                  <small>{item.taskTitle} · {item.input_summary || 'Agent execution'}</small>
                  {item.output_summary && (
                    <small>Output: {item.output_summary.slice(0, 180)}</small>
                  )}
                  {item.error_summary && (
                    <small className="error">{item.error_summary}</small>
                  )}
                  {item.started_at && (
                    <small>{new Date(item.started_at).toLocaleString()}</small>
                  )}
                </div>
                <span className={`badge ${statusClass(item.status)}`}>
                  {item.status}
                </span>
              </div>
            ))
        )}
      </section>

      <section className="panel execution-panel">
        <div className="panel-head">
          <div>
            <h2>Activity timeline</h2>
            <p className="muted">Recent events across your tasks.</p>
          </div>
          <Clock3 size={18}/>
        </div>

        {allActivity.length === 0 ? (
          <div className="empty">
            <b>No activity recorded yet</b>
            <p className="muted">
              Task planning, execution and verification events will appear here.
            </p>
          </div>
        ) : (
          allActivity.slice(0, 30).map((item, index) => (
            <div className="activity-line" key={`${item.taskId}-${index}`}>
              <span className="status-dot"/>
              <div>
                <b>{item.message}</b>
                <small>{item.taskTitle}</small>
                <small>
                  {item.created_at
                    ? new Date(item.created_at).toLocaleString()
                    : 'Time unavailable'}
                </small>
              </div>
            </div>
          ))
        )}
      </section>

      <div className="muted">
        {lastUpdated
          ? `Last updated: ${lastUpdated.toLocaleTimeString()}`
          : 'Activity has not been loaded yet.'}
        {' '}Use Refresh activity to fetch the latest records.
      </div>
    </div>
  );
}

function HomePage() {
  const features = [
    {
      icon: Bot,
      title: 'AI Task Planning',
      text: 'Turn complex goals into structured tasks, subtasks and actionable plans.'
    },
    {
      icon: Search,
      title: 'Research Agent',
      text: 'Research topics using web search, collect evidence and create sourced reports.'
    },
    {
      icon: FileText,
      title: 'Document Generation',
      text: 'Create structured reports, proposals and professional documents.'
    },
    {
      icon: Database,
      title: 'Data Analysis',
      text: 'Upload datasets, inspect data quality, explore patterns and generate insights.'
    },
    {
      icon: ListTodo,
      title: 'Project Planning',
      text: 'Organize milestones, dependencies and project execution workflows.'
    },
    {
      icon: CheckCircle2,
      title: 'Verification',
      text: 'Review completed work for consistency, completeness and potential issues.'
    },
    {
      icon: GraduationCap,
      title: 'Exam Solver',
      text: 'Extract questions from papers and generate worked solutions for review.'
    },
    {
      icon: Activity,
      title: 'Agent Activity',
      text: 'Monitor recorded agent executions, task progress and activity history.'
    }
  ];

  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link to="/" className="brand">
          <span className="brand-mark">T</span>
          <span>TaskForge<small>AI WORKSPACE</small></span>
        </Link>

        <nav className="landing-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#agents">AI capabilities</a>
        </nav>

        <div className="landing-actions">
          <Link to="/login" className="landing-login">Log in</Link>
          <Link to="/register" className="primary link-button">
            Get started
          </Link>
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="hero-content">
            <span className="hero-label">
              <Sparkles size={15}/> INTELLIGENT TASK EXECUTION PLATFORM
            </span>

            <h1>
              From complex tasks
              <span> to meaningful results.</span>
            </h1>

            <p>
              Meet TaskForge — an AI-powered workspace designed to plan,
              research, analyze and organize your work through specialized
              AI capabilities.
            </p>

            <div className="hero-buttons">
              <Link to="/register" className="primary link-button">
                Get started free <ArrowLeft size={16} style={{transform:'rotate(180deg)'}}/>
              </Link>
              <a href="#features" className="secondary link-button">
                Explore features
              </a>
            </div>

            <div className="hero-trust">
              <span><CheckCircle2 size={15}/> Structured workflows</span>
              <span><CheckCircle2 size={15}/> AI-assisted productivity</span>
              <span><CheckCircle2 size={15}/> One workspace</span>
            </div>
          </div>

          <div className="hero-visual">
            <div className="preview-window">
              <div className="preview-top">
                <div className="preview-dots"><i/><i/><i/></div>
                <span>TaskForge Workspace</span>
                <span className="preview-live">Workspace preview</span>
              </div>

              <div className="preview-body">
                <div className="preview-sidebar">
                  <div className="preview-logo">T</div>
                  <span><LayoutDashboard size={17}/></span>
                  <span><ListTodo size={17}/></span>
                  <span><Bot size={17}/></span>
                  <span><Search size={17}/></span>
                  <span><FileText size={17}/></span>
                </div>

                <div className="preview-main">
                  <small>YOUR WORKSPACE</small>
                  <h3>Good work starts here.</h3>
                  <p>Organize your ideas and get work moving.</p>

                  <div className="preview-stats">
                    <div><small>Total tasks</small><b>12</b></div>
                    <div><small>AI agents</small><b>06</b></div>
                    <div><small>Workflows</small><b>08</b></div>
                  </div>

                  <div className="preview-task">
                    <div className="preview-task-icon"><Search size={16}/></div>
                    <div><b>Market research</b><small>Research workflow</small></div>
                    <span>Research</span>
                  </div>
                  <div className="preview-task">
                    <div className="preview-task-icon"><FileText size={16}/></div>
                    <div><b>Generate project report</b><small>Document workflow</small></div>
                    <span>Documents</span>
                  </div>
                  <div className="preview-task">
                    <div className="preview-task-icon"><Database size={16}/></div>
                    <div><b>Analyze dataset</b><small>Data workflow</small></div>
                    <span>Analysis</span>
                  </div>
                </div>
              </div>
            </div>
            <p className="preview-caption">Illustrative workspace preview</p>
          </div>
        </section>

        <section className="landing-section" id="features">
          <div className="landing-section-heading">
            <span className="hero-label">WHAT TASKFORGE CAN DO</span>
            <h2>Everything you need to move work forward.</h2>
            <p>
              A collection of AI-powered tools designed to support your
              workflow from planning to final review.
            </p>
          </div>

          <div className="landing-feature-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <article className="landing-feature-card" key={feature.title}>
                  <div className="landing-feature-icon">
                    <Icon size={21}/>
                  </div>
                  <span className="feature-number">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <h3>{feature.title}</h3>
                  <p>{feature.text}</p>
                </article>
              );
            })}
          </div>
        </section>

        <section className="landing-process" id="how-it-works">
          <div className="landing-section-heading">
            <span className="hero-label">SIMPLE WORKFLOW</span>
            <h2>From an idea to an organized outcome.</h2>
            <p>Follow a clear process to manage your work.</p>
          </div>

          <div className="process-grid">
            <div className="process-card">
              <span>01</span><Sparkles size={23}/>
              <h3>Create a task</h3>
              <p>Describe your goal and expected outcome.</p>
            </div>
            <div className="process-card">
              <span>02</span><ListTodo size={23}/>
              <h3>Plan the work</h3>
              <p>Break the goal into manageable subtasks.</p>
            </div>
            <div className="process-card">
              <span>03</span><Bot size={23}/>
              <h3>Use AI capabilities</h3>
              <p>Run the relevant specialist workflows.</p>
            </div>
            <div className="process-card">
              <span>04</span><CheckCircle2 size={23}/>
              <h3>Review results</h3>
              <p>Inspect outputs and verify completed work.</p>
            </div>
          </div>
        </section>

        <section className="landing-agent-section" id="agents">
          <div>
            <span className="hero-label">ONE CONNECTED WORKSPACE</span>
            <h2>Different capabilities. One destination.</h2>
            <p>
              TaskForge brings planning, research, document creation,
              data analysis and verification into a unified workspace.
            </p>
          </div>
          <div className="agent-pills">
            {['Planner','Research','Document','Data Analysis',
              'Project Planning','Verification'].map(agent => (
              <span key={agent}><Bot size={15}/>{agent}</span>
            ))}
          </div>
        </section>

        <section className="landing-cta">
          <span className="hero-label">START BUILDING WITH TASKFORGE</span>
          <h2>Make your next task your best workflow.</h2>
          <p>Create your workspace and explore TaskForge.</p>
          <Link to="/register" className="primary link-button">
            Create your account <ArrowLeft size={16} style={{transform:'rotate(180deg)'}}/>
          </Link>
        </section>
      </main>

      <footer className="landing-footer">
        <Link to="/" className="brand">
          <span className="brand-mark">T</span>
          <span>TaskForge<small>AI WORKSPACE</small></span>
        </Link>
        <span>AI-powered task execution workspace.</span>
        <span>© {new Date().getFullYear()} TaskForge</span>
      </footer>
    </div>
  );
}

function ComingSoon({title,desc}){return <div className="page"><div className="eyebrow">TASKFORGE WORKSPACE</div><h1>{title}</h1><p className="muted">{desc}</p><div className="panel coming"><div className="soft-icon large"><Bot size={26}/></div><h2>This module is being built</h2><p className="muted">The interface and integration will be added in the next development milestone. No simulated agent results are shown here.</p></div></div>}

function Protected() {
  const { user } = useAuth();

  if (user) {
    return (
      <Shell>
        <Routes>
          <Route path="/" element={<Dashboard/>}/>
          <Route path="/tasks" element={<Tasks/>}/>
          <Route path="/tasks/:taskId" element={<TaskDetail/>}/>
          <Route path="/agents" element={<AgentActivity/>}/>
          <Route path="/research" element={<ResearchStudio/>}/>
          <Route path="/documents" element={<DocumentStudio/>}/>
          <Route path="/data" element={<DataAnalysisStudio/>}/>
          <Route path="/exam-solver" element={<ExamSolverStudio/>}/>
          <Route path="*" element={<Navigate to="/"/>}/>
        </Routes>
      </Shell>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<HomePage/>}/>
      <Route path="/login" element={<AuthPage mode="login"/>}/>
      <Route path="/register" element={<AuthPage mode="register"/>}/>
      <Route path="*" element={<Navigate to="/"/>}/>
    </Routes>
  );
}
export default function App(){return <AuthProvider><Protected/></AuthProvider>}
