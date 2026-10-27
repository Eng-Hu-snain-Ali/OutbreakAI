CREATE TABLE region (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    risk VARCHAR(20) NOT NULL,
    active_cases INTEGER DEFAULT 0,
    active_trend VARCHAR(20) DEFAULT '+0%',
    patients INTEGER DEFAULT 0,
    patients_trend VARCHAR(20) DEFAULT '+0%',
    history TEXT DEFAULT '[]',
    disease VARCHAR(100),
    population_density DOUBLE PRECISION,
    hospital_capacity DOUBLE PRECISION,
    vaccination_rate DOUBLE PRECISION,
    recommendations TEXT,
    last_week_cases INTEGER
);

INSERT INTO region (city, risk, active_cases, active_trend, patients, patients_trend, history) VALUES 
('Karachi', 'High', 642, '+14%', 1847, '+12%', '[410, 448, 487, 521, 558, 601, 642]'),
('Lahore', 'Medium', 284, '+5%', 923, '+5%', '[220, 235, 248, 261, 270, 278, 284]'),
('Islamabad', 'Low', 47, '-2%', 134, '-3%', '[62, 58, 55, 52, 50, 48, 47]'),
('Peshawar', 'Medium', 198, '+8%', 567, '+8%', '[150, 160, 165, 175, 182, 190, 198]'),
('Quetta', 'Low', 31, '-1%', 89, '-2%', '[40, 38, 36, 35, 33, 32, 31]'),
('Multan', 'High', 521, '+18%', 1423, '+19%', '[300, 340, 390, 430, 470, 500, 521]');
