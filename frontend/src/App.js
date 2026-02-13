// src/App.js

import React, { useState, useEffect, useCallback } from 'react';
import { Container, CircularProgress, Box, Typography } from '@mui/material';
import Header from './components/Header';
import Filters from './components/Filters';
import StockTable from './components/StockTable';
import { fetchStockData } from './services/api';

function App() {
  const [filters, setFilters] = useState({
    Williams_R_21: { from: '', to: '' },
    EMA_13_Williams_R: { from: '', to: '' },
    RSI_14: { from: '', to: '' },
    RSI_21: { from: '', to: '' },
  });
  const [stockData, setStockData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const getStockData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchStockData(filters);
      console.log('Fetched stock data:', data); // Debugging line
      setStockData(data);
    } catch (err) {
      setError('Failed to fetch stock data. Please try again later.');
      console.error('Error fetching stock data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Callback for DataRefreshButton to trigger data reload
  const handleDataRefreshed = useCallback(() => {
    console.log('Data refresh completed - reloading stock data');
    setRefreshTrigger(prev => prev + 1);
  }, []);

  useEffect(() => {
    getStockData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, refreshTrigger]);

  return (
    <div>
      <Header onDataRefreshed={handleDataRefreshed} />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Filters filters={filters} setFilters={setFilters} />
        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" sx={{ mt: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Typography color="error" variant="h6" align="center" sx={{ mt: 4 }}>
            {error}
          </Typography>
        ) : (
          <StockTable data={stockData} />
        )}
      </Container>
    </div>
  );
}

export default App;
