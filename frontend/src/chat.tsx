import React, { useEffect, useState } from 'react';
import PromptSubmit from './components/PromptSubmit/PromptSubmit';
import Message from './components/Message/Message';
import Loader from './components/Common/Loader';

interface PromptData {
  prompt: string | null;
  bot: any;
}

function Chat() {
  const [list, setList] = useState<PromptData[]>([])
  const [isloading, setIsLoading] = useState<boolean>(false)
  const [userId, setUserId] = useState("")
  const [userName, setUserName] = useState("")
  useEffect(() => {
    setUserId(localStorage.getItem("userId")||"")
    setUserName(localStorage.getItem("name")||"")
    if(list.length === 0 && localStorage.getItem("conversation")) {
      const conversation = localStorage.getItem("conversation") || ""
      setList(JSON.parse(conversation))
    }
    console.log(isloading, 'list')
  }, [isloading, list.length, userName])
  return (
    <div className='flex-1'>
      {/* <h1 className='pb-7 font-semibold'>ChatBot (ReactJS + Django + OpenAi)</h1> */}
      <div className='border-black flex-1 border-2 bg-[#ECECEC] rounded-md h-screen' style={{paddingBottom: '60'}}>
        <ul className='py-3 px-2 overflow-y-auto h-screen' style={{paddingBottom: '75px'}} >
          {list.map(item => {
            return (
              <>
                <Message key={`${Math.random()}-${Date.now()}`} item={item} />
              </>
            )
          })}
          <li>
           {isloading && <div className='flex justify-center items-center'><Loader /></div>}
          </li>
          <PromptSubmit isloading={isloading} setIsLoading={setIsLoading} setList={setList} list={list} userId={userId}/>
        </ul>

      </div>

    </div>
  );
}

export default Chat;
