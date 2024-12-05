import unittest
from fastapi import Depends
from crud import transfer_funds
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app import models

class TestMathFunctions(unittest.TestCase):

    def test_add(self,db: Session = Depends(get_db)):
        self.assertEqual(transfer_funds(
            db, 
            from_account_id=1, 
            to_account_id=2, 
            amount=100
        ), models.Transaction(
            from_account_id=1,
            to_account_id=2,
            amount=100,
            status="completed"
        )) 

    #def test_subtract(self):
    #    self.assertEqual(subtract(10, 5), 5)
    #    self.assertEqual(subtract(0, 5), -5)

    def test_add_type_error(self,db: Session = Depends(get_db)):
        with self.assertRaises(ValueError):  # Проверяем, что вызывается ошибка
            transfer_funds(
            db, 
            from_account_id=3, 
            to_account_id=2, 
            amount=100
        )

if __name__ == '__main__':
    unittest.main()
