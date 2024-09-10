from core.database import queue, availability_collection
from fastapi import HTTPException

class QueueManager:
    def __init__(self, avg_consultation_time: int):
        self.db = queue
        self.avg_consultation_time = avg_consultation_time

    async def add_to_queue(self, patient_id: str, patient_name: str):
        try:
            queue_size = await self.db.count_documents({})
            position = queue_size + 1
            estimated_time = position * self.avg_consultation_time
            
            slot = {
                "patient_id": patient_id,
                "patient_name": patient_name,
                "queue_position": position,
                "estimated_time": estimated_time
            }
            
            result = await self.db.insert_one(slot)
            slot["_id"] = str(result.inserted_id)
            return slot

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding patient to queue: {str(e)}")

    async def next_patient(self):
        try:
            first_patient = await self.db.find_one_and_delete({}, sort=[("queue_position", 1)])
            if first_patient:
                patients = self.db.find({}).sort("queue_position", 1)
                position = 1
                async for patient in patients:
                    new_position = position
                    new_estimated_time = position * self.avg_consultation_time
                    await self.db.update_one(
                        {"_id": patient["_id"]},
                        {"$set": {
                            "queue_position": new_position,
                            "estimated_time": new_estimated_time
                        }}
                    )
                    position += 1
            else:
                raise HTTPException(status_code=404, detail="No patients in the queue")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error moving to the next patient: {str(e)}")


    async def get_queue_status(self):
        try:
            patients = await self.db.find({}).sort("queue_position", 1).to_list(None)
            for patient in patients:
                patient["_id"] = str(patient["_id"])
            return patients

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching queue status: {str(e)}")

async def check_availability(availability: dict):
    try:
        availability["day"] = availability["day"].isoformat()

        existing_availability = await availability_collection.find_one({"doctor_id": availability["doctor_id"]})
        
        if existing_availability:
            await availability_collection.update_one(
                {"doctor_id": availability["doctor_id"]},
                {"$set": {"day": availability["day"], "time_slots": availability["time_slots"], "Available": availability["Available"]}}
            )
        else:
            result = await availability_collection.insert_one(availability)
            
        doctor_id = availability["doctor_id"]
        
        return {"message": f"Availability set for doctor {str(result.inserted_id)}", "availability": availability}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking or setting availability: {str(e)}")
