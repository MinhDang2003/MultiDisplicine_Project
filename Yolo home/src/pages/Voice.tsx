import { useState, useEffect, useRef } from "react";
import { useTheme } from "@mui/material";
import Sidebarr from "../component/Sidebar";
import 'regenerator-runtime/runtime';
import { tokens } from "../theme.tsx";

const styles = {
    container: {
        textAlign: 'center',
        marginTop: '20px',
    },
    button: {
        padding: '10px 20px',
        borderRadius: '5px',
        cursor: 'pointer',
        fontWeight: 'bold',
        margin: '10px',
    },
    message: {
        marginTop: '20px',
        fontWeight: 'bold',
        color: 'black',
    },
    canvas: {
        margin: '20px auto',
        display: 'block',
    },
};

function VoiceRecognitionPage() {
    const [recognition, setRecognition] = useState(null);
    const [listening, setListening] = useState(false);
    const [message, setMessage] = useState('');
    const [understood, setUnderstood] = useState(false);
    const audioContextRef = useRef(null);
    const analyserRef = useRef(null);
    const dataArrayRef = useRef(null);
    const animationFrameRef = useRef(null);

    useEffect(() => {
        if (!('webkitSpeechRecognition' in window)) {
            setMessage('Your browser does not support speech recognition.');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = false;
        recognitionInstance.interimResults = false;
        recognitionInstance.lang = 'en-US';

        recognitionInstance.onstart = () => {
            setListening(true);
            setMessage('Listening...');
        };

        recognitionInstance.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;
            setMessage(`You said: ${speechResult}`);
            setUnderstood(true);
            setListening(false);
        };

        recognitionInstance.onerror = (event) => {
            setMessage(`Error occurred in recognition: ${event.error}`);
            setUnderstood(false);
            setListening(false);
        };

        recognitionInstance.onend = () => {
            setListening(false);
        };

        setRecognition(recognitionInstance);
    }, []);

    const startListening = async () => {
        if (listening) {
            recognition.stop();
            stopAudioProcessing();
        } else {
            recognition.start();
            await startAudioProcessing();
        }
    };

    const startAudioProcessing = async () => {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);
        source.connect(analyserRef.current);
        visualize();
    };

    const stopAudioProcessing = () => {
        if (audioContextRef.current) {
            audioContextRef.current.close();
            audioContextRef.current = null;
        }
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
    };

    const visualize = () => {
        if (analyserRef.current) {
            analyserRef.current.getByteFrequencyData(dataArrayRef.current);
            const canvas = document.getElementById("audio-canvas");
            const canvasCtx = canvas.getContext("2d");
            const WIDTH = canvas.width;
            const HEIGHT = canvas.height;
            canvasCtx.clearRect(0, 0, WIDTH, HEIGHT);

            const barWidth = (WIDTH / analyserRef.current.frequencyBinCount) * 2.5;
            let barHeight;
            let x = 140; // Offset added here

            for (let i = 0; i < analyserRef.current.frequencyBinCount; i++) {
                barHeight = dataArrayRef.current[i];
                canvasCtx.fillStyle = 'black';
                canvasCtx.fillRect(x, HEIGHT - barHeight / 2, barWidth, barHeight / 2);
                x += barWidth + 1;
            }

            animationFrameRef.current = requestAnimationFrame(visualize);
        }
    };

    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    return (
        <div className="flex h-screen w-screen min-h-screen items-start overflow-y-auto">
            <div className="sticky h-screen left-0 top-0">
                <Sidebarr />
            </div>
            <div className="grow body w-screen h-screen">
                <h1 className="text-black font-serif text-center text-7xl">Voice Recognition</h1>
                <div className="mt-5 items-center bg-[#DAC0A3] shadow-xl" style={styles.container}>
                    <canvas id="audio-canvas" width="600" height="100" style={styles.canvas}></canvas>
                    <button
                        onClick={startListening}
                        style={{
                            ...styles.button,
                            backgroundColor: listening ? 'white' : 'black',
                            color: '#DAC0A3'
                        }}
                    >
                        {listening ? 'Stop Voice Recognition' : 'Start Voice Recognition'}
                    </button>
                    <div style={styles.message}>
                        {message}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default VoiceRecognitionPage;
