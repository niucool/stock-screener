// src/components/StockTable.js

import React, { useState } from 'react';
import {
  DataGrid,
  GridToolbarContainer,
  GridToolbarExport,
} from '@mui/x-data-grid';
import { Box, Typography, Alert, AlertTitle } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import StockDetailDialog from './StockDetailDialog'; // Ensure this path is correct

const StockTable = ({ data }) => {
  const [selectedStock, setSelectedStock] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Ensure data is an array to prevent crashes
  if (!Array.isArray(data)) {
    console.error('StockTable Error: data is not an array:', data);
    let debugInfo = '';
    try {
      debugInfo = JSON.stringify(data).slice(0, 200);
    } catch (e) {
      debugInfo = String(data);
    }
    return (
      <Alert severity="error">
        <AlertTitle>Error: Invalid Data Format</AlertTitle>
        Expected an array but received: <strong>{typeof data}</strong>
        <br />
        <code style={{ display: 'block', marginTop: '10px', whiteSpace: 'pre-wrap' }}>
          {debugInfo}
        </code>
      </Alert>
    );
  }

  // Define the columns for the DataGrid with updated field names
  const columns = [
    { field: 'Symbol', headerName: 'Symbol', width: 100 },
    { field: 'Date', headerName: 'Date', width: 130 },
    {
      field: 'Close',
      headerName: 'Close Price',
      width: 130,
      type: 'number',
      // Temporarily remove valueFormatter
      // valueFormatter: (params) =>
      //   params.value !== undefined && params.value !== null
      //     ? `$${params.value.toFixed(2)}`
      //     : 'N/A',
    },
    {
      field: 'Williams_R_21', // Updated field name
      headerName: 'Williams %R (21)',
      width: 150,
      type: 'number',
      // Temporarily remove valueFormatter
      // valueFormatter: (params) =>
      //   params.value !== undefined && params.value !== null
      //     ? params.value.toFixed(2)
      //     : 'N/A',
    },
    {
      field: 'EMA_13_Williams_R', // Updated field name
      headerName: 'EMA(13) of Williams %R',
      width: 180,
      type: 'number',
      // Temporarily remove valueFormatter
      // valueFormatter: (params) =>
      //   params.value !== undefined && params.value !== null
      //     ? params.value.toFixed(2)
      //     : 'N/A',
    },
    {
      field: 'RSI_14',
      headerName: 'RSI 14',
      width: 100,
      type: 'number',
      // Temporarily remove valueFormatter
      // valueFormatter: (params) =>
      //   params.value !== undefined && params.value !== null
      //     ? params.value.toFixed(2)
      //     : 'N/A',
    },
    {
      field: 'RSI_21',
      headerName: 'RSI 21',
      width: 100,
      type: 'number',
      // Temporarily remove valueFormatter
      // valueFormatter: (params) =>
      //   params.value !== undefined && params.value !== null
      //     ? params.value.toFixed(2)
      //     : 'N/A',
    },
  ];

  // Map the incoming data to the format expected by DataGrid
  const rows = data.map((item, index) => ({
    id: index, // DataGrid requires a unique 'id' for each row
    Symbol: item.Symbol || 'N/A',
    Date: item.Date || 'N/A',
    Close: item.Close !== undefined ? Number(item.Close) : null,
    Williams_R_21: item.Williams_R_21 !== undefined ? Number(item.Williams_R_21) : null,
    EMA_13_Williams_R: item.EMA_13_Williams_R !== undefined ? Number(item.EMA_13_Williams_R) : null,
    RSI_14: item.RSI_14 !== undefined ? Number(item.RSI_14) : null,
    RSI_21: item.RSI_21 !== undefined ? Number(item.RSI_21) : null,
  }));

  // Debugging: Log the mapped rows
  console.log('Mapped Rows:', rows);

  // Check data age - show warning if data is stale
  const getDataAgeWarning = () => {
    if (rows.length === 0 || !data[0]) return null;

    const firstStock = data[0];
    const dataDate = firstStock.Date ? new Date(firstStock.Date) : null;
    const dataAgeDays = firstStock.Data_Age_Days;

    if (!dataDate) return null;

    // Show warning if data is older than 3 days
    if (dataAgeDays > 3) {
      const severity = dataAgeDays > 30 ? 'error' : 'warning';

      return (
        <Alert
          severity={severity}
          icon={<WarningAmberIcon />}
          sx={{ mb: 2 }}
        >
          <AlertTitle>
            {dataAgeDays > 30 ? 'Critical: Data is Very Stale' : 'Warning: Data May Be Outdated'}
          </AlertTitle>
          Stock data is <strong>{dataAgeDays} days old</strong> (last updated: <strong>{firstStock.Date}</strong>).
          {dataAgeDays > 100 && (
            <> This likely indicates a <strong>system date issue</strong>.
              Please verify your system clock is set correctly before refreshing data.</>
          )}
          {' '}Click the <strong>"Refresh Data"</strong> button in the header to update with the latest market data.
        </Alert>
      );
    }

    return null;
  };

  // Custom toolbar with export functionality
  const CustomToolbar = () => (
    <GridToolbarContainer>
      <GridToolbarExport csvOptions={{ allColumns: true }} />
    </GridToolbarContainer>
  );

  // Handle row click to open the detail dialog
  const handleRowClick = (params) => {
    setSelectedStock(params.row);
    setDialogOpen(true);
  };

  // Handle closing the detail dialog
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedStock(null);
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Data age warning */}
      {getDataAgeWarning()}

      <Box sx={{ height: 600, width: '100%' }}>
        {rows.length > 0 ? (
          <DataGrid
            rows={rows}
            columns={columns}
            pageSize={25}
            rowsPerPageOptions={[25, 50, 100]}
            components={{
              Toolbar: CustomToolbar,
            }}
            disableSelectionOnClick
            onRowClick={handleRowClick}
          />
        ) : (
          <Typography variant="h6" align="center" sx={{ mt: 4 }}>
            No data available.
          </Typography>
        )}
      </Box>

      {/* Detail Dialog */}
      <StockDetailDialog
        open={dialogOpen}
        handleClose={handleCloseDialog}
        stock={selectedStock}
      />
    </Box>
  );
};

export default StockTable;
