import pytest
from rutabaga.rooms.users import User #gestion utilisateur et connexion
from rutabaga.rooms.salles import Salle #gestion utilisateur et connexion
from datetime import datetime

# Afin de protéger les mdp, ils sont stockés dans un fichier
# secret.txt qui est dans le gitignore

with open("secret.txt") as f:
    login = f.readline().strip()
    password = f.readline().strip()

user = User(login, password)


class Test_salles_occupees:
    def test_one(self):
        start_dt = datetime(2025, 9, 1, 9, 0)
        start_dt.strftime("%Y-%m-%d %H:%M")
        end_dt = datetime(2025, 9, 1, 13, 0)
        end_dt.strftime("%Y-%m-%d %H:%M")
        
        user = User(login, password)
        salles_occ = user.salles_occupees(start=start_dt, end= end_dt)
        assert set(salles_occ) == {'1002', '2005', '1004', 'Amphi200', 'Amphi250', '2041'}

    def test_two(self):
        start_dt = datetime(2025, 9, 2, 13, 0)
        start_dt.strftime("%Y-%m-%d %H:%M")
        end_dt = datetime(2025, 9, 2, 13, 15)
        end_dt.strftime("%Y-%m-%d %H:%M")
        
        user = User(login, password)
        salles_occ = user.salles_occupees(start=start_dt, end= end_dt)
        assert set(salles_occ) == {'2005'}
        
    def test_tree(self):
        start_dt = datetime(2025, 9, 3, 17, 0)
        start_dt.strftime("%Y-%m-%d %H:%M")
        end_dt = datetime(2025, 9, 3, 19, 0)
        end_dt.strftime("%Y-%m-%d %H:%M")
        
        user = User(login, password)
        salles_occ = user.salles_occupees(start=start_dt, end= end_dt)
        assert set(salles_occ) == {'1004', '2042', '2001', '2009', 'Amphi250', '2047'}


class Test_ensemble_salles:
    def test_one(self):
        start_dt = datetime(2025, 9, 1, 7, 0)
        start_dt.strftime("%Y-%m-%d %H:%M")
        end_dt = datetime(2025, 9, 1, 8, 0)
        end_dt.strftime("%Y-%m-%d %H:%M")

        user = User(login, password)
        salles_occ = user.salles_occupees(start=start_dt, end= end_dt)
        assert salles_occ == []

    def test_two(self):
        start_dt = datetime(2025, 9, 1, 7, 0)
        start_dt.strftime("%Y-%m-%d %H:%M")
        end_dt = datetime(2025, 9, 1, 8, 0)
        end_dt.strftime("%Y-%m-%d %H:%M")

        user = User(login, password)
        salles_libres = user.salles_libres(start=start_dt, end= end_dt)
        assert set(salles_libres) == {'2027', '2028', '2030', '2032', '2034', '2036', '2040', '2041', 
        '2029i/2031i', '2035', '2035', '2037i/2039i', '2026', '2042', '2043', '2024i', '2044i', '2045', 
        '2023', '2022i', '2046i', '2047', '2021', '2048i', '2020', '2019i', '2018', '2017', '2012', '2007i', 
        '2001', '2016', '2015i', '2014i', '2010', '2009', '2008i', '2006', '2005', '2003', '2002'}
