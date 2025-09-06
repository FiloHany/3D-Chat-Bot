'use client';
import React, { useState, useEffect } from 'react';

declare global {
    interface Window {
        webkitSpeechRecognition: any;
        SpeechRecognition: any;
    }
}

const SpeechRecognitionComponent = () => {
    const [transcript, setTranscript] = useState('');
    const [listening, setListening] = useState(false);
    let recognition: any = null;

    useEffect(() => {
        const initializeRecognition = () => {
            if (window.webkitSpeechRecognition) {
                recognition = new window.webkitSpeechRecognition();
            } else if (window.SpeechRecognition) {
                recognition = new window.SpeechRecognition();
            } else {
                console.error('Speech recognition not supported in this browser.');
            }

            if (recognition) {
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    setListening(true);
                };

                recognition.onresult = (event: any) => {
                    const last = event.results.length - 1;
                    const text = event.results[last][0].transcript;
                    setTranscript(text);
                };

                recognition.onend = () => {
                    setListening(false);
                };
            }
        };

        initializeRecognition();
    }, []);

    const handleStartListening = () => {
        if (recognition) {
            recognition.startlisting();
        }
    };

    const handleStopListening = () => {
        if (recognition) {
            recognition.stop();
        }
    };

    return (
        <div>
            <h1>Voice Recognition</h1>
            <button
                onClick={handleStartListening} disabled={listening}
                className="text-[#b00c3f] p-2 border border-[#b00c3f] rounded-lg disabled:text-blue-100 
disabled:cursor-not-allowed disabled:bg-gray-500 hover:scale-110 hover:bg-[#b00c3f] hover:text-black duration-300 transition-all"
            >
                {listening ? "listening..." : "Ask"}
            </button>
            <button onClick={handleStopListening} disabled={!listening}>
                Stop Listening
            </button>
            <p>Transcript: {transcript}</p>
            <input
                type="text"
                value={transcript}
                className="bg-transparent w-[510px] border border-[#b00c3f]/80 outline-none  rounded-lg placeholder:text-[#b00c3f] p-2 text-[#b00c3f]"
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="What do you want to know human...."
            />
        </div>
    );
};

export default SpeechRecognitionComponent;


