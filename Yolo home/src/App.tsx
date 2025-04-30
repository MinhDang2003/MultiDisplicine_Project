import Login from './pages/LoginPage.tsx';
import SignUp from './pages/SignUpPage.tsx';
import Home from './pages/Home.tsx';
import {Route,  Routes} from "react-router-dom";
import Layout from './component/Layout.tsx';
import Missing from './pages/Missing.tsx';
import RequireAuth from './component/RequireAuth.tsx';
import Dashboard from './pages/Dashboard.tsx';
import PersistLogin from './component/PersistLogin.tsx';
import WebcamCapture from './pages/TestCam.tsx'
import Users from './component/Users.tsx';
import VoiceRecognitionPage from './pages/Voice.tsx';
function App() {
  

  return (
    <>
      
        
        <Routes>
          <Route path='/' element={<Layout/>}>
            {/* Public */ }
            <Route path='/login' element={<Login></Login>}/>
            <Route path='/signup' element={<SignUp></SignUp>}/>
            {/* Protected */ }
            <Route element = {<PersistLogin></PersistLogin>}>
              <Route element={<RequireAuth></RequireAuth>}>
                <Route path='/' element={<Home></Home>}/>
                <Route path='/Dashboard' element={<Dashboard></Dashboard>}/>
                <Route path='/CamTest' element={<WebcamCapture></WebcamCapture>}></Route>
                <Route path='/Users' element={<Users></Users>}></Route>
                <Route path='/Voice' element={<VoiceRecognitionPage></VoiceRecognitionPage>}></Route>
              </Route>
            </Route>
            
            {/* catch all to Missing */ }
            <Route path='*' element={<Missing></Missing>}/>
          </Route>
          
          
        </Routes>
      
    </>
  )
}

export default App
