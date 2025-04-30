import IconMapping from "../Utils/MappingIcon";
import DevicesAPI from "../api_copy/DeviceApi";
import RoomsAPI from"../api_copy/RoomsApi";

async function getAllRoomsData(){
    const data = await RoomsAPI.getAllRooms()
    let res =  data.data.rooms.map((item)=>({"devices":item.appliances, "room_id":item.room_id}))
    let result = []
    for (var i in res)
        result.push(res[i])
    result[0].selected = true 
    return result
}
async function processSignalData(data){
    let res = {...data}
    let signal = {
        labels: [],
        datasets: [{
            data: [],
            fill: false,
            pointRadius: 0,
            borderColor: data.key.includes("temperature")?"Orange":"Blue"
        }]
    }
    for (var key in await data.data) {
        signal.labels.push(key)
        signal.datasets[0].data.push(Number(data.data[key].value))
    }
    res.data = signal
    return res
}

async function getDevicesOfRoom(room_id) {
    const data = await RoomsAPI.getDevicesByRoomID(room_id)
    let devices = {devices:[],signal:[]}
    for (var i in data.data.rooms.appliances) {
        const device = data.data.rooms.appliances[i] 
        if (device.app_id.includes( "humidity") || device.app_id.includes("temperature")) {
            const signal = await processSignalData(device)
            devices.signal.push([signal,data.data.rooms.room_id])
        }  
        else
            devices.devices.push([device,data.data.rooms.room_id])
    }
    return devices
}

async function toggleDevice(roomID, devide_id,currValue,type) {

    const state = `${(Number(currValue))}`
    const res = await DevicesAPI.setStateDevice(roomID,devide_id,state,type)
    return res
}
export {getAllRoomsData,getDevicesOfRoom,toggleDevice};