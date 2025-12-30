// src/components/Header.js

import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import DataRefreshButton from './DataRefreshButton';

const Header = ({ onDataRefreshed }) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <ShowChartIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          S&P 500 Stock Screener
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <DataRefreshButton onDataRefreshed={onDataRefreshed} />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; // Ensure default export
