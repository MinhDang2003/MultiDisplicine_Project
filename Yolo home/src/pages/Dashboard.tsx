import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Users from "../component/Users";
import 'regenerator-runtime/runtime';
import DevicesAPI from "../api_copy/DeviceApi";
import { useTheme } from "@mui/material";
import Sidebarr from "../component/Sidebar";
import RoomBar from '../component/bars/rooms/RoomsBar';
import DevicesBar from '../component/bars/devices/DevicesBar';
import { getAllRoomsData, getDevicesOfRoom, toggleDevice } from '../business/HomePageData';
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';
import RoomsApi from '../api_copy/RoomsApi';
import DeviceApi from '../api_copy/DeviceApi';
import { tokens } from "../theme.tsx";

const styles = {
    modal: {
        position: 'relative',
        padding: '20px',
        border: '2px solid black',
        borderRadius: '10px',
        backgroundColor: '#f9f9f9',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        marginTop: '30px',
    },
    label: {
        color: 'black',
        backgroundColor: 'beige',
        padding: '10px',
        borderRadius: '5px',
        fontWeight: 'bold',
        marginBottom: '10px',
        width: '100%',
        textAlign: 'left',
    },
    input: {
        backgroundColor: 'white',
        color: 'black',
        border: '2px solid black',
        borderRadius: '5px',
        padding: '10px',
        width: '100%',
        boxSizing: 'border-box',
        marginBottom: '15px',
    },
    submitButton: {
        backgroundColor: 'beige',
        color: 'black',
        border: '2px solid black',
        borderRadius: '5px',
        padding: '10px 20px',
        cursor: 'pointer',
        fontWeight: 'bold',
    },
    closeButton: {
        position: 'absolute',
        top: '10px',
        right: '10px',
        backgroundColor: 'black',
        color: 'white',
        border: 'none',
        borderRadius: '0%',
        width: '30px',
        height: '30px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        fontWeight: 'bold',
        fontSize: '20px',
        lineHeight: '20px',
    },
    errorMessage: {
        color: 'red',
        fontWeight: 'bold',
        textAlign: 'center',
    },
};

function Dashboard() {
    const [inputs, setInputs] = useState({});
    const [triggerRender, setTriggerRender] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [count, setCount] = useState(0);
    const [data, setData] = useState([]);
    const [selectedRoom, setSelectedRoom] = useState("{:::}");
    const [toggleData, setToggleData] = useState(null);
    const [devicesData, setDevicesData] = useState({ signal: [], devices: [] });

    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({ ...values, [name]: value }));
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>, close: () => void) => {
        event.preventDefault();
        try {
            if (event.target.name === "addRoom") {
                await RoomsApi.addRoom(inputs.roomID);
            } else if (event.target.name === "removeRoom") {
                await RoomsApi.removeRoom(inputs.roomID);
            } else if (event.target.name === "addDevice") {
                await DeviceApi.addDevice(selectedRoom, inputs.deviceID, inputs.deviceType, inputs.feedID);
            } else if (event.target.name === "removeDevice") {
                await DeviceApi.removeDevice(selectedRoom, inputs.deviceID);
            }
            setTriggerRender(!triggerRender);
            close();
        } catch (error) {
            console.error('Error:', error);
            setError((error as Error).response.data.msg || 'An error occurred');
            close();
        }
    };

    const closeErrorPopup = () => {
        setError(null);
    };
    
    useEffect(() => {
        const source = new EventSource('http://127.0.0.1:8090/stream');
        
        
        source.onmessage = function() {
            setTimeout(() => setCount(prevCount => (prevCount + 1) % 2), 1000);
            
            console.log((count + 1) % 2)
          console.log(count)
        };
        return () => {
        
          source.close();
        };
      },[]);  // Empty dependency array means this effect runs once on mount and clean up on unmount

    useEffect(() => {
        console.log("4")
        const getData = async () => {
            const res = await getAllRoomsData();
            setData(res);
            if (selectedRoom === "{:::}" || !res.some((item) => item.room_id === selectedRoom)) {
                setSelectedRoom(res[0].room_id);
            }
        };
        getData();
    }, [triggerRender]);

    useEffect(() => {
        console.log("9999")
        const getData = async () => {
            const res = await getDevicesOfRoom(selectedRoom);
            console.log(res)
            setDevicesData(res);
        };
        getData();
    }, [selectedRoom, count]);

    useEffect(() => {
        console.log("2")
        if (toggleData) {
            const toggle = async () => {
                console.log("example")
                console.log(toggleData)
                const res = await toggleDevice(toggleData[0], toggleData[1], toggleData[2], toggleData[3]);
                if (res) {
                    setTimeout(() => setCount((count + 1) % 2), 1000);

                }
            };
            toggle();
        }
    }, [toggleData]);


    const theme = useTheme();
    const colors = tokens(theme.palette.mode);

    return (
        <div className="flex h-screen w-screen min-h-screen items-start overflow-y-auto">
            <div className="sticky h-screen left-0 top-0">
                <Sidebarr />
            </div>
            <div className="grow body w-screen h-screen">
                <h1 className="text-black font-serif text-center text-7xl">Dashboard</h1>
                <div className="mt-5 items-center bg-[#DAC0A3] shadow-xl">
                    <div className="flex justify-between items-center">
                        <h1 className="text-black font-serif ml-4">Rooms</h1>
                        <div className="flex space-x-4 mr-4">
                            <Popup trigger={<button className="p-2 bg-black text-[#DAC0A3] rounded" style={{ width: '160px', height: '40px' }}>&#43; Add Room</button>} modal nested>
                                {close => (
                                    <div className='modal' style={styles.modal}>
                                        <button onClick={close} style={styles.closeButton}>
                                            &times;
                                        </button>
                                        <form name="addRoom" onSubmit={(event) => handleSubmit(event, close)} style={styles.form}>
                                            <label style={styles.label}>
                                                Enter room ID to add:
                                            </label>
                                            <input
                                                style={styles.input}
                                                type="text"
                                                name="roomID"
                                                value={inputs.roomID || ""}
                                                onChange={handleChange}
                                            />
                                            <input
                                                type="submit"
                                                style={styles.submitButton}
                                            />
                                        </form>
                                    </div>
                                )}
                            </Popup>
                            <Popup trigger={<button className="p-2 bg-black text-[#DAC0A3] rounded" style={{ width: '160px', height: '40px' }}>&#8722; Remove Room</button>} modal nested>
                                {close => (
                                    <div className='modal' style={styles.modal}>
                                        <button onClick={close} style={styles.closeButton}>
                                            &times;
                                        </button>
                                        <form name="removeRoom" onSubmit={(event) => handleSubmit(event, close)} style={styles.form}>
                                            <label style={styles.label}>
                                                Enter room ID to remove:
                                            </label>
                                            <input
                                                style={styles.input}
                                                type="text"
                                                name="roomID"
                                                value={inputs.roomID || ""}
                                                onChange={handleChange}
                                            />
                                            <input
                                                type="submit"
                                                style={styles.submitButton}
                                            />
                                        </form>
                                    </div>
                                )}
                            </Popup>
                        </div>
                    </div>
                    <RoomBar data={[data, selectedRoom, setSelectedRoom]} />
                </div>
                <div className="mt-5 items-center bg-[#DAC0A3] shadow-xl">
                    <div className="flex justify-between items-center">
                        <h1 className="text-black font-serif ml-4">Devices</h1>
                        <div className="flex space-x-4 mr-4">
                            <Popup trigger={<button className="p-2 bg-black text-[#DAC0A3] rounded" style={{ width: '160px', height: '40px' }}>&#43; Add Device</button>} modal nested>
                                {close => (
                                    <div className='modal' style={styles.modal}>
                                        <button onClick={close} style={styles.closeButton}>
                                            &times;
                                        </button>
                                        <form name="addDevice" onSubmit={(event) => handleSubmit(event, close)} style={styles.form}>
                                            <label style={styles.label}>
                                                Selected Room ID: {selectedRoom}
                                            </label>
                                            <label style={styles.label}>
                                                Enter device ID to add:
                                                <input
                                                    style={styles.input}
                                                    type="text"
                                                    name="deviceID"
                                                    value={inputs.deviceID || ""}
                                                    onChange={handleChange}
                                                />
                                            </label>
                                            <label style={styles.label}>
                                                Enter the device type:
                                                <input
                                                    style={styles.input}
                                                    type="text"
                                                    name="deviceType"
                                                    value={inputs.deviceType || ""}
                                                    onChange={handleChange}
                                                />
                                            </label>
                                            <label style={styles.label}>
                                                Enter the feed ID:
                                                <input
                                                    style={styles.input}
                                                    type="text"
                                                    name="feedID"
                                                    value={inputs.feedID || ""}
                                                    onChange={handleChange}
                                                />
                                            </label>
                                            <input
                                                type="submit"
                                                style={styles.submitButton}
                                            />
                                        </form>
                                    </div>
                                )}
                            </Popup>

                            <Popup trigger={<button className="p-2 bg-black text-[#DAC0A3] rounded" style={{ width: '160px', height: '40px' }}>&#8722; Remove Device</button>} modal nested>
                                {close => (
                                    <div className='modal' style={styles.modal}>
                                        <button onClick={close} style={styles.closeButton}>
                                            &times;
                                        </button>
                                        <form name="removeDevice" onSubmit={(event) => handleSubmit(event, close)} style={styles.form}>
                                            <label style={styles.label}>
                                                Selected Room ID: {selectedRoom}
                                            </label>
                                            <label style={styles.label}>
                                                Enter device ID to remove:
                                                <input
                                                    style={styles.input}
                                                    type="text"
                                                    name="deviceID"
                                                    value={inputs.deviceID || ""}
                                                    onChange={handleChange}
                                                />
                                            </label>
                                            <input
                                                type="submit"
                                                style={styles.submitButton}
                                            />
                                        </form>
                                    </div>
                                )}
                            </Popup>

                        </div>
                    </div>
                    <DevicesBar data={[devicesData.devices, setToggleData]} />
                </div>
                {error && (
                    <Popup open={true} onClose={closeErrorPopup} modal>
                        <div className="modal" style={styles.modal}>
                            <button onClick={closeErrorPopup} style={styles.closeButton}>&times;</button>
                            <div style={styles.errorMessage}>{error}</div>
                        </div>
                    </Popup>
                )}
            </div>
        </div>
    );
}

export default Dashboard;
