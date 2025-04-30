import { useState, useEffect, useRef } from "react";
import "../App.css";
import tempicon from "../assets/temperature.png";
import humidicon from "../assets/humidity.png";
import brighticon from "../assets/brightness.png";
import { axiosPublic } from "../api/axios";
import {
	Chart as ChartJS,
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
} from "chart.js";
import { Line } from "react-chartjs-2";
import Sidebarr from "../component/Sidebar";
import Popup from "reactjs-popup";
import "reactjs-popup/dist/index.css";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement);

const styles = {
	modal: {
		position: "relative",
		padding: "20px",
		border: "2px solid black",
		borderRadius: "10px",
		backgroundColor: "#f9f9f9",
	},
	closeButton: {
		position: "absolute",
		top: "10px",
		right: "10px",
		backgroundColor: "black",
		color: "white",
		border: "none",
		borderRadius: "0%",
		width: "30px",
		height: "30px",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		cursor: "pointer",
		fontWeight: "bold",
		fontSize: "20px",
		lineHeight: "20px",
	},
	errorMessage: {
		color: "red",
		fontWeight: "bold",
		textAlign: "center",
	},
};

function Home() {
	const stateList = ["Temperature", "Humidity", "Brightness"];
	const modeList = ["Day", "Week", "Month"];

	const [currentTemperature, setCurrentTemperature] = useState(0);
	const [currentHumidity, setCurrentHumidity] = useState(0);
	const [currentBrightness, setCurrentBrightness] = useState(0);

	const [temperatureDay, setTemperatureDay] = useState<number[]>([]);
	const [humidityDay, setHumidityDay] = useState<number[]>([]);
	const [brightnessDay, setBrightnessDay] = useState<number[]>([]);

	const [temperatureWeek, setTemperatureWeek] = useState<number[]>([]);
	const [humidityWeek, setHumidityWeek] = useState<number[]>([]);
	const [brightnessWeek, setBrightnessWeek] = useState<number[]>([]);

	const [temperatureMonth, setTemperatureMonth] = useState<number[]>([]);
	const [humidityMonth, setHumidityMonth] = useState<number[]>([]);
	const [brightnessMonth, setBrightnessMonth] = useState<number[]>([]);

	const [monthLabel, setMonthLabel] = useState<string[]>([]);
	const [weekLabel, setWeekLabel] = useState<string[]>([]);
	const [dayLabel, setDayLabel] = useState<string[]>([]);

	const [popupMessage, setPopupMessage] = useState<string | null>(null);
	const [isTempWarning, setIsTempWarning] = useState(false);
	const [isBrightnessWarning, setIsBrightnessWarning] = useState(false);
	const getCurrentStat = async () => {
		try {
			const responseTemp = await axiosPublic.post("/api/current_temperature");
			setCurrentTemperature(Number(responseTemp.data.value).toFixed(2));

			const responseHumid = await axiosPublic.post("/api/current_humidity");
			setCurrentHumidity(Number(responseHumid.data.value).toFixed(2));

			const responseBrightness = await axiosPublic.post(
				"/api/current_brightness"
			);
			setCurrentBrightness(Number(responseBrightness.data.value).toFixed(2));
		} catch (error) {
			console.log(error);
		}
	};
	const closePopup = () => {
		setPopupMessage(null); // Close the popup
		hasPopupShown.current = true; // Reset the flag
	};
	// Add a new state variable
	// Add a new state variable
	// Replace useState with useRef
	const hasPopupShown = useRef(false);

	const checkConditions = () => {
		let warningMessages = []; // Array to hold warning messages
		console.log(hasPopupShown.current);
        if (currentTemperature > 40) {
            if (!hasPopupShown.current) {
                warningMessages.push("Warning: Temperature is above 40°C");
            }
            setIsTempWarning(true); // Set temperature warning state to true
        } else if (currentTemperature < 20) {
            if (!hasPopupShown.current) {
                warningMessages.push("Warning: Temperature is below 20°C");
            }
            setIsTempWarning(true); // Set temperature warning state to true
        } else {
            setIsTempWarning(false); // Set temperature warning state to false
        }

        if (currentBrightness > 80) {
            if (!hasPopupShown.current) {
                warningMessages.push("Warning: Brightness is above 80%");
            }
            setIsBrightnessWarning(true); // Set brightness warning state to true
        } else if (currentBrightness < 20) {
            if (!hasPopupShown.current) {
                warningMessages.push("Warning: Brightness is below 20%");
            }
            setIsBrightnessWarning(true); // Set brightness warning state to true
        } else {
            setIsBrightnessWarning(false); // Set brightness warning state to false
        }

        if (warningMessages.length > 0) {
            setPopupMessage(warningMessages.join("<br />")); // Join warning messages with a newline
        } else {
            setPopupMessage(null);
        }
	};
	useEffect(() => {
		getCurrentStat();
		const interval = setInterval(() => {
			getCurrentStat();
			checkConditions();
		}, 1000);

		fetchData(0); // Fetch initial data for day mode
		fetchData(1);
		fetchData(2);

		return () => clearInterval(interval); // Cleanup interval on unmount
	}, [currentTemperature, currentBrightness]);

	const fetchData = async (option: number) => {
		try {
			const responseTemp = await axiosPublic.post("/api/temperature", {
				option,
			});
			const dataTemp = responseTemp.data;

			const responseHumid = await axiosPublic.post("/api/humidity", { option });
			const dataHumid = responseHumid.data;

			const responseBrightness = await axiosPublic.post("/api/brightness", {
				option,
			});
			const dataBrightness = responseBrightness.data;

			if (option === 0) {
				const tempArray = dataTemp.temperature.map((item) => item.value);
				setTemperatureDay(tempArray);

				const humidArray = dataHumid.humidity.map((item) => item.value);
				setHumidityDay(humidArray);

				const brightArray = dataBrightness.brightness.map((item) => item.value);
				setBrightnessDay(brightArray);

				const extractedArray = dataBrightness.brightness.map(
					(item) => item.hour
				);
				setDayLabel(extractedArray);
			} else if (option === 1) {
				const tempArray = dataTemp.temperature.map((item) => item.value);
				setTemperatureWeek(tempArray);

				const humidArray = dataHumid.humidity.map((item) => item.value);
				setHumidityWeek(humidArray);

				const brightArray = dataBrightness.brightness.map((item) => item.value);
				setBrightnessWeek(brightArray);

				const extractedArray = dataBrightness.brightness.map(
					(item) => item.date
				);
				setWeekLabel(extractedArray);
			} else if (option === 2) {
				const tempArray = dataTemp.temperature.map((item) => item.value);
				setTemperatureMonth(tempArray);

				const humidArray = dataHumid.humidity.map((item) => item.value);
				setHumidityMonth(humidArray);

				const brightArray = dataBrightness.brightness.map((item) => item.value);
				setBrightnessMonth(brightArray);

				const extractedArray = dataBrightness.brightness.map(
					(item) => item.date
				);
				setMonthLabel(extractedArray);
			}
		} catch (error) {
			console.log(error);
		}
	};

	const labelList = [dayLabel, weekLabel, monthLabel];
	const dataList = [
		[temperatureDay, temperatureWeek, temperatureMonth],
		[humidityDay, humidityWeek, humidityMonth],
		[brightnessDay, brightnessWeek, brightnessMonth],
	];

	const [state, setState] = useState(0);
	const [mode, setMode] = useState(0);

	const labels = labelList[mode].map((label) => label.toString());

	const options = {
		responsive: true,
	};

	const initData = {
		labels,
		datasets: [
			{
				data: dataList[state][mode],
				borderColor: "rgb(255, 99, 132)",
				backgroundColor: "rgba(255, 99, 132, 0.5)",
			},
		],
	};
	const [data, setData] = useState(initData);

	const toggleState = (num: number) => {
		setState(() => {
			const newState = num;
			updateDataAndLabels(newState, mode);
			return newState;
		});
	};

	const toggleMode = (num: number) => {
		setMode(() => {
			const newMode = num;
			updateDataAndLabels(state, newMode);
			return newMode;
		});
	};

	const updateDataAndLabels = (newState: number, newMode: number) => {
		const labels = labelList[newMode].map((label) => label.toString());
		const data = {
			labels,
			datasets: [
				{
					data: dataList[newState][newMode],
					borderColor: "rgb(255, 99, 132)",
					backgroundColor: "rgba(255, 99, 132, 0.5)",
				},
			],
		};
		setData(data);
	};

	return (
		<div className="flex h-screen w-screen min-h-screen items-start overflow-y-auto">
			<div className="sticky h-screen left-0 top-0">
				<Sidebarr />
			</div>
			<div className="grow body w-screen h-screen">
				<h1 className="text-black font-serif text-center text-7xl">Home</h1>
				<div className="flex flex-wrap justify-center field1 bg-[#DAC0A3] shadow-xl">
					<div
						className={`flex flex-col p-0 mx-auto justify-center h-64 w-64 items-center field1Item rounded-3xl bg-black ${
							isTempWarning ? "warning" : ""
						}`}
						style={isTempWarning ? { backgroundColor: "#EE4E4E" } : {}}
					>
						<img src={tempicon} className="h-32 w-32" />
						<div>{currentTemperature}C</div>
					</div>
					<div className="flex flex-col p-0 mx-auto justify-center h-64 w-64 items-center field1Item rounded-3xl bg-black">
						<img src={humidicon} className="h-32 w-32" />
						<div>{currentHumidity}%</div>
					</div>
					<div
						className={`flex flex-col p-0 mx-auto justify-center h-64 w-64 items-center field1Item rounded-3xl bg-black ${
							isBrightnessWarning ? "warning" : ""
						}`}
						style={isBrightnessWarning ? { backgroundColor: "#EE4E4E" } : {}}
					>
						<img src={brighticon} className="h-32 w-32" />
						<div>{currentBrightness}%</div>
					</div>
				</div>
				<div className="mt-5 items-center bg-[#DAC0A3] shadow-xl">
					<div>
						<h1 className="text-black"> History Log</h1>

						<button className="m-5 w-40" onClick={() => toggleState(0)}>
							{"Temperature"}
						</button>
						<button className="m-5 w-40" onClick={() => toggleState(1)}>
							{"Humidity"}
						</button>
						<button className="m-5 w-40" onClick={() => toggleState(2)}>
							{"Brightness"}
						</button>
					</div>
					<div>
						<button className="m-5 w-40" onClick={() => toggleMode(0)}>
							{"Day"}
						</button>
						<button className="m-5 w-40" onClick={() => toggleMode(1)}>
							{"Week"}
						</button>
						<button className="m-5 w-40" onClick={() => toggleMode(2)}>
							{"Month"}
						</button>
					</div>
					<div className="flex flex-col justify-center items-center showGraph bg-inherit text-black">
						<div style={{ height: "auto", width: "100%" }}>
							<h1>{stateList[state]}</h1>
						</div>
						<div
							className="line-graph"
							style={{ width: "90%", height: "auto" }}
						>
							<Line options={options} data={data} />
						</div>
						<div
							className="flex flex-row justify-center items-center mode-buttons"
							style={{ height: "auto", width: "100%" }}
						>
							<div style={{ height: "auto", width: "100px" }}>
								<h2>{modeList[mode]}</h2>
							</div>
						</div>
					</div>
				</div>
			</div>
			{popupMessage && (
				<Popup
					open={true}
					closeOnDocumentClick
					onClose={closePopup}
				>
					<div style={styles.modal}>
						<button
							style={styles.closeButton}
							onClick={closePopup}
						>
							×
						</button>
						<div
							style={styles.errorMessage}
							dangerouslySetInnerHTML={{ __html: popupMessage }}
						/>
					</div>
				</Popup>
			)}
		</div>
	);
}

export default Home;
