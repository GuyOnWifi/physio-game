import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import refreshButton from '/start.svg'
import { useEffect, useState, useRef } from 'react'

import './MainPage.css'


function MainPage() {
    const [frame, setFrame] = useState<string>('')
    const [moves, setMoves] = useState<Array<number> | null>([0, 1, 2, 3]);
    const [removing, setRemoving] = useState<number | null>(null);
    const [scoringEffect, setScoringEffect] = useState<number | null>(null); // Set to null initially
    const [score, setScore] = useState<number>(0); // State variable for score
    const [currentPose, setCurrentPose] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0);

    const finalScore = useRef<number>(-1);
    const lastExecuted = useRef<number>(0);

    useEffect(() => {
        lastExecuted.current = Date.now();

        const intervalId = setInterval(() => {
            setRemoving(0);
            setTimeout(() => {
                setMoves(prevMoves => {
                    // Create a new array to avoid mutating the state directly
                    let newMoves = [...prevMoves!.slice(1)];
                    newMoves.push(Math.floor(Math.random() * 4));

                    setRemoving(-1);

                    return newMoves;
                });
            }, 300)
            console.log(finalScore.current);
            lastExecuted.current = Date.now();

            const updateScore = async () => {
                try {
                    const response = await fetch('http://localhost:3000/update_score', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ scoringEffect: finalScore.current }),
                    });
                    const data = await response.json();
                    setScore(data.score); // Update score in frontend
                } catch (error) {
                    console.error('Error updating score:', error);
                }
            };

            if (finalScore.current >= 0) updateScore();

        }, 5000);


        return () => {
            clearInterval(intervalId);
        };
    }, []);


    useEffect(() => {
        const interval = setInterval(async () => {
            setTimeRemaining(Date.now() - lastExecuted.current);

            try {
                const response = await fetch('http://localhost:3000/get_scoring_effect');
                const data = await response.json();
                setScoringEffect(data.scoringEffect);
                finalScore.current = data.scoringEffect;
            } catch (error) {
                console.error('Error getting scoring effect:', error);
            }
        }, 100); // Poll every 100ms

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        document.body.style.backgroundImage = "url('/bg.svg')";
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundPosition = 'center center';

        return () => {
            document.body.style.backgroundImage = "";
        };
    }, []);

    useEffect(() => {
        if (moves && moves.length > 0) {
            fetch('http://localhost:3000/current_pose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ poseValue: moves[0] }),
            });
        }
    }, [moves]);

    const stateOptions = [
        { text: 'X', color: 'text-[#FF0000] text-5xl' },
        { text: 'Okay', color: 'text-[#FF8800] text-5xl' },
        { text: 'Great!', color: 'text-[#00FF80] text-6xl' },
        { text: 'PERFECT!', color: 'text-[#00FFE5] text-7xl ml-12' },
    ]

    return (

        <div className=''>

            <div className='w-full text-white text-center text-5xl pt-10'>
                <h1> Phys.io </h1>
            </div>

            <div className="w-full h-[30rem] flex">
                <div className="w-1/6 h-full ">
                    {scoringEffect && <div className={`w-full h-full ${stateOptions[scoringEffect - 1].color} flex items-center justify-center font-bold transform -rotate-12`}>
                        <p>{stateOptions[scoringEffect - 1].text}</p>
                    </div>}
                </div>

                <div className="w-4/6 h-full text-white flex flex-col items-center justify-center">
                    {/* Placeholder for Camera */}
                    <div className="w-[60%] h-[80%] bg-gray-700 border-2 border-gray-500 rounded-md flex items-center justify-center">
                        <img src="http://localhost:3000/video_feed" alt="Camera Feed" className="w-full h-full object-cover" />
                    </div>
                    <img src={refreshButton} alt="Refresh Button" className='mt-4' onClick={() => { setMoves(Array.from({ length: 4 }, () => Math.floor(Math.random() * 4))) }} />
                </div>

                {/* Right Section */}
                <div className="w-1/6 h-full text-[#FFD504] flex flex-col justify-start pl-4 pt-24 tracking-wider text-5xl font-bold">
                    <h2 className="text-2xl ">SCORE: </h2>
                    <div className="text-4xl font-bold ml-4 ">{score}</div>
                </div>
            </div>

            {frame && <img src={frame} alt="Camera Feed" />}

            <h1 className="text-white asbolute bottom-0" onClick={() => {
                setRemoving(0);
                setTimeout(() => {
                    let newMoves = moves?.slice(1)!;
                    newMoves.push(Math.floor(Math.random() * 4))

                    setMoves(newMoves);
                    setRemoving(-1);
                }, 300)
            }}>

            </h1>

            {moves && <div id="moves" className="absolute flex flex-row gap-2 border-b-[0.5px] border-white bottom-[5%] right-0 w-[50vw] h-[20vh]">
                {moves.slice(0, 3).map((val, idx) => {
                    let src = ""

                    if (val === 0) {
                        src = "/poses/DownwardDog.png";
                    } else if (val === 1) {
                        src = "/poses/TreePose.png"
                    } else if (val === 2) {
                        src = "/poses/Warrior1.png"
                    } else if (val === 3) {
                        src = "/poses/Warrior2.png"
                    }

                    return (
                        <img src={src} key={idx} className={`bg-gradient-to-t from-white/20 to-transparent to-60% dance-move uration-300 ease-out ${idx === removing ? "removed" : ""}`} />
                    )
                })}
            </div>
            }

            <div id="progress-bar" className="absolute bottom-[5%] border-2 border-white w-[100px] h-[20px] overflow-hidden">
                <div id="bar" className="bg-white h-[20px]" style={{width: 100 - (timeRemaining / 50)}}></div>
            </div>
        </div>
    )
}

export default MainPage