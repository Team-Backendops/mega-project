from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from models.queue import DoctorAvailability, JoinQueue
from crud.queue import QueueManager, check_availability

router = APIRouter()

queue_manager = QueueManager(avg_consultation_time=10)

@router.post("/doctors/{doctor_id}/availability/")
async def set_doctor_availability(doctor_id: str, availability: DoctorAvailability,current_user: UserModel = Depends(get_current_user):
    try:
        availability_dict = {
            "doctor_id": doctor_id,
            "day": availability.day,
            "time_slots": availability.time_slots,
            "Available": availability.Available,
            "max_patients": availability.max_patients,
            "avg_consultation_time": availability.avg_consultation_time 
        }

        current_availability = await check_availability(availability_dict)
        return {"message": f"Availability set for doctor {doctor_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting doctor availability: {str(e)}")

from fastapi import APIRouter, HTTPException
from core.database import availability_collection

@router.get("/doctors/{doctor_id}/availability/")
async def get_doctor_availability(doctor_id: str,current_user: UserModel = Depends(get_current_user):
    try:
        doctor_availability = await availability_collection.find_one({"doctor_id": doctor_id})
        
        if doctor_availability:
            doctor_availability['day'] = str(doctor_availability['day'])

            if "_id" in doctor_availability:
                doctor_availability["_id"] = str(doctor_availability["_id"])

            return {"doctor_id": doctor_id, "availability": doctor_availability}
        else:
            raise HTTPException(status_code=404, detail=f"Availability not found for doctor {doctor_id}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctor availability: {str(e)}")


# Patient joins the queue
@router.post("/doctors/{doctor_id}/queue/join/")
async def join_queue(doctor_id: str, patient: JoinQueue,current_user: UserModel = Depends(get_current_user):
    try:
        slot = await queue_manager.add_to_queue(patient.patient_id, patient.patient_name)
        return {"message": f"Patient {patient.patient_name} added to queue", "slot": slot}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding patient to queue: {str(e)}")


# Get current queue status
@router.get("/doctors/{doctor_id}/queue/")
async def get_queue_status(doctor_id: str,current_user: UserModel = Depends(get_current_user):
    try:
        queue_status = await queue_manager.get_queue_status()
        return {"queue": queue_status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving queue status: {str(e)}")


# Doctor moves to the next patient
@router.post("/doctors/{doctor_id}/queue/next/")
async def move_to_next_patient(doctor_id: str,current_user: UserModel = Depends(get_current_user):
    try:
        await queue_manager.next_patient()
        queue_status = await queue_manager.get_queue_status()
        return {"message": "Moved to the next patient", "queue": queue_status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moving to the next patient: {str(e)}")


# WebSocket for real-time queue updates
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_update(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending message to connection: {str(e)}")

manager = ConnectionManager()

@router.websocket("/doctors/{doctor_id}/queue/ws/")
async def queue_updates(websocket: WebSocket, doctor_id: str):
    try:
        await manager.connect(websocket)
        while True:
            try:
                queue_status = await queue_manager.get_queue_status()
                await websocket.send_json(queue_status)
            except Exception as e:
                print(f"Error sending queue status: {str(e)}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error during WebSocket connection: {str(e)}")
