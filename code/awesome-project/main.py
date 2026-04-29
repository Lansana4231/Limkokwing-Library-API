import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Limkokwing Library API")

# Mock Data
BOOKS = {
    "101": {"title": "Introduction to Python", "author": "Guido van Rossum", "status": "available", "category": "Technology"},
    "102": {"title": "Data Science Handbook", "author": "Jake VanderPlas", "status": "available", "category": "Data Science"},
    "103": {"title": "Clean Code", "author": "Robert C. Martin", "status": "available", "category": "Software Engineering"}
}

LOANS: Dict[str, str] = {}  # book_id: user_id

class BorrowRequest(BaseModel):
    book_id: str
    user_id: str

class ReturnRequest(BaseModel):
    book_id: str
    user_id: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Limkokwing Library API. Visit /docs for documentation."}

@app.get("/books")
async def search_books(q: Optional[str] = None, category: Optional[str] = None):
    """Search for books by title, author, or category."""
    await asyncio.sleep(0.1)  # Simulate small I/O delay
    results = []
    for k, v in BOOKS.items():
        match = True
        if q:
            if q.lower() not in v['title'].lower() and q.lower() not in v['author'].lower():
                match = False
        if category and category.lower() != v['category'].lower():
            match = False
        
        if match:
            results.append({"id": k, **v})
    return results

@app.post("/borrow")
async def borrow_book(request: BorrowRequest):
    """Borrow a book with concurrency handling."""
    # Simulate network latency
    await asyncio.sleep(random.uniform(0.1, 0.5))
    
    book_id = request.book_id
    user_id = request.user_id

    if book_id not in BOOKS:
        raise HTTPException(status_code=404, detail="Book not found.")
    
    if book_id in LOANS:
        raise HTTPException(status_code=400, detail=f"Book already borrowed by {LOANS[book_id]}.")
    
    # Process loan
    LOANS[book_id] = user_id
    BOOKS[book_id]["status"] = "borrowed"
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    return {
        "status": "success",
        "message": f"Book '{BOOKS[book_id]['title']}' borrowed successfully.",
        "due_date": due_date
    }

@app.post("/return")
async def return_book(request: ReturnRequest):
    """Return a book."""
    book_id = request.book_id
    user_id = request.user_id

    if book_id in LOANS and LOANS[book_id] == user_id:
        del LOANS[book_id]
        BOOKS[book_id]["status"] = "available"
        return {"status": "success", "message": "Book returned successfully.", "fine": 0.0}
    
    raise HTTPException(status_code=400, detail="Loan record not found for this user/book.")

@app.get("/users/{user_id}/fines")
async def get_fines(user_id: str):
    """Track overdue books and fines."""
    # Simulation: User_C has an overdue book
    if user_id == "User_C":
        return {
            "user_id": user_id,
            "overdue_books": [{"book_id": "103", "title": "Clean Code", "days_overdue": 5}],
            "total_fines": 25.00
        }
    return {"user_id": user_id, "overdue_books": [], "total_fines": 0.00}

# Simulation mode (Part B requirement)
async def run_simulation():
    """Simulates multiple users accessing the system at the same time."""
    print("--- Starting Concurrent Simulation ---")
    
    # Mock requests
    tasks = [
        borrow_book(BorrowRequest(book_id="101", user_id="User_A")),
        borrow_book(BorrowRequest(book_id="102", user_id="User_B")),
        borrow_book(BorrowRequest(book_id="101", user_id="User_C"))
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, res in enumerate(results):
        print(f"Request {i+1}: {res}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        asyncio.run(run_simulation())
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
