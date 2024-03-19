import React, { useState } from 'react';

interface PromptData {
    prompt: string | null;
    bot: any;
}

const Message = ({ item }: any) => {
    const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);

    const handleMouseDown = (message: string) => {
        setLongPressTimer(setTimeout(() => handleLongPress(message), 1000)); // Adjust the duration as needed
    };

    const handleMouseUp = () => {
        if (longPressTimer) {
            clearTimeout(longPressTimer);
            setLongPressTimer(null);
        }
    };

    const handleLongPress = async (message: string) => {
        try {
            await navigator.clipboard.writeText(message);
            alert('Message copied to clipboard!');
        } catch (error) {
            console.error('Failed to copy message:', error);
        }
    };

    return (
        <li className='flex flex-col'>
            <div className='flex justify-end gap-1 pb-3 pl-9'>
                <span className='flex items-end text-xs'>me</span>
                <span
                    className={`bg-[#703BF7] text-white px-2 min-w-[40px] flex justify-center py-2 rounded-md`}
                    onMouseDown={() => handleMouseDown(item.prompt)}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                >
                    {item.prompt}
                </span>
            </div>

            {/* Conditionally render bot messages */}
            {Array.isArray(item.bot) ? (
                item.bot.map((botMessage: string, index: number) => (
                    <div key={index} className='flex justify-start gap-1 pb-3 pr-9'>
                        <span className='flex items-start text-xs w-[30px]'>
                            <img className='w-full' src="/images/bot.png" alt="bot"/>
                        </span>
                        <span className='bg-white px-2 py-2 max-w-[277px] rounded-md'>
                            {botMessage}
                        </span>
                    </div>
                ))
            ) : (
                <div className='flex justify-start gap-1 pb-3 pr-9'>
                    <span className='flex items-start text-xs w-[30px]'>
                        <img className='w-full' src="/images/bot.png" alt="bot"/>
                    </span>
                    <span className='bg-white px-2 py-2 max-w-[277px] rounded-md'>
                        {item.bot}
                    </span>
                </div>
            )}
        </li>
    );
};

export default Message;
