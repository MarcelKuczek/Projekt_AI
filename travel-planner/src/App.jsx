import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import TravelForm from './components/TravelForm'
import TravelPlan from './components/TravelPlan'
import ChatAboutPlan from "./components/ChatAboutPlan"
import DownloadPdfButton from './components/DownloadPdfButton'

function App() {
  const[formData, setFormData] = useState({});
  const[plan, setPlan] = useState(null);
  const[isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (payload) => {
    setPlan(null);
    setIsLoading(true);
    try{
      const res = await fetch("http://127.0.0.1:8000/api/generate-plan", {
        method:'POST',
        headers:{
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setPlan(data)
      console.log(data)
    } catch (error){
      console.error(error);
    } finally {


      setIsLoading(false);
    }
  }


  return (
    <div>
      <h1>Twój Planer Wyjazdu</h1>
      <TravelForm onSubmit={handleSubmit}/>
      {isLoading && <div className="loader">Generuję nowy plan podróży...</div>}
      {plan && !isLoading && (
        <>
          <TravelPlan plan={plan}/>
          <ChatAboutPlan plan={plan}/>
          <DownloadPdfButton plan={plan} />
        </>
      )}
    </div>
  )
}

export default App
