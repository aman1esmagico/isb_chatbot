import React, { useState } from 'react'
import { SubmitIcon } from '../Common/Icons';


interface PromptData {
    prompt: string | null;
    bot: any;
}

type SetListFunction = React.Dispatch<React.SetStateAction<PromptData[]>>;
type SetLoeadingFunction = React.Dispatch<React.SetStateAction<boolean>>;

interface PromptSubmitProps {
  setList: SetListFunction;
  list: PromptData[];
  isloading: boolean;
  setIsLoading: SetLoeadingFunction;
  userId: string
}

const PromptSubmit: React.FC<PromptSubmitProps> = ({list, setList, isloading, setIsLoading, userId}) => {
    const [prompt, setPrompt] = useState<string>("")

    const submitHandler = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setIsLoading(true)
        if (prompt.trim() === ""){
            console.log("no text provided")
            setIsLoading(false)
            return
        }
        try {
            const response = await fetch('http://127.0.0.1:8000/api/chatbot/talk/', {
                method: "POST",
                body:JSON.stringify({ prompt: prompt, userId: parseInt(userId)}),
                headers: {
                    "Content-Type": "application/json"
                }
            })
            const data = await response.json()
            const newList = [...list, {prompt, bot: data['message']}]
            setList(newList)
            console.log(list)
            localStorage.setItem("conversation", JSON.stringify(newList))
            setIsLoading(false)
            setPrompt("")
        } catch(error) {
            console.log(error)
        }
    }

    return (
        <div className='absolute bottom-0 w-full mb-1'>
            <form onSubmit={submitHandler} className='relative' style={{display: 'flex'}}>
                {isloading && <label className='bg-[#d2cfcf] text-white px-2 w-full'>Asking...</label>} 
                <input style={{flex: 1}} className='w-full py-3 pl-2 pr-[50px] outline-none rounded-b-sm' value={prompt} onChange={(e) => setPrompt(e.target.value)} type="text" placeholder='Enter prompt' />
                <button disabled={isloading} type='submit' className='right-4 bottom-0 top-0'><SubmitIcon /></button>
            </form>
        </div>
    )
}

export default PromptSubmit
