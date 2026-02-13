// src/components/Filters.js

import React from 'react';
import { Grid, TextField, Button, Box } from '@mui/material';

const FILTER_RANGES = {
  Williams_R_21: { from: -100, to: 0 },
  EMA_13_Williams_R: { from: -100, to: 100 },
  RSI_14: { from: 0, to: 100 },
  RSI_21: { from: 0, to: 100 },
};

const Filters = ({ filters, setFilters }) => {
  // Handle changes for from and to inputs
  const handleChange = (e) => {
    // The name will be something like "Williams_R_21_from"
    // We need to split by the LAST underscore to separate field from bound
    const { name, value } = e.target;
    const lastUnderscoreIndex = name.lastIndexOf('_');
    const field = name.substring(0, lastUnderscoreIndex);
    const bound = name.substring(lastUnderscoreIndex + 1);

    setFilters((prev) => ({
      ...prev,
      [field]: {
        ...prev[field],
        [bound]: value === '' ? '' : Number(value),
      },
    }));
  };

  // Handle reset functionality
  const handleReset = () => {
    setFilters({
      Williams_R_21: { from: '', to: '' },
      EMA_13_Williams_R: { from: '', to: '' },
      RSI_14: { from: '', to: '' },
      RSI_21: { from: '', to: '' },
    });
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        {/* Williams %R Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="Williams %R From"
            variant="outlined"
            fullWidth
            name="Williams_R_21_from"
            value={filters.Williams_R_21.from}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.Williams_R_21.from,
                max: FILTER_RANGES.Williams_R_21.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.Williams_R_21.from} to ${FILTER_RANGES.Williams_R_21.to}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="Williams %R To"
            variant="outlined"
            fullWidth
            name="Williams_R_21_to"
            value={filters.Williams_R_21.to}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.Williams_R_21.from,
                max: FILTER_RANGES.Williams_R_21.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.Williams_R_21.from} to ${FILTER_RANGES.Williams_R_21.to}`}
          />
        </Grid>

        {/* EMA(13) of Williams %R Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="EMA(13) Williams %R From"
            variant="outlined"
            fullWidth
            name="EMA_13_Williams_R_from"
            value={filters.EMA_13_Williams_R.from}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.EMA_13_Williams_R.from,
                max: FILTER_RANGES.EMA_13_Williams_R.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.EMA_13_Williams_R.from} to ${FILTER_RANGES.EMA_13_Williams_R.to}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="EMA(13) Williams %R To"
            variant="outlined"
            fullWidth
            name="EMA_13_Williams_R_to"
            value={filters.EMA_13_Williams_R.to}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.EMA_13_Williams_R.from,
                max: FILTER_RANGES.EMA_13_Williams_R.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.EMA_13_Williams_R.from} to ${FILTER_RANGES.EMA_13_Williams_R.to}`}
          />
        </Grid>

        {/* RSI 14 Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="RSI 14 From"
            variant="outlined"
            fullWidth
            name="RSI_14_from"
            value={filters.RSI_14.from}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.RSI_14.from,
                max: FILTER_RANGES.RSI_14.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.RSI_14.from} to ${FILTER_RANGES.RSI_14.to}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="RSI 14 To"
            variant="outlined"
            fullWidth
            name="RSI_14_to"
            value={filters.RSI_14.to}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.RSI_14.from,
                max: FILTER_RANGES.RSI_14.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.RSI_14.from} to ${FILTER_RANGES.RSI_14.to}`}
          />
        </Grid>

        {/* RSI 21 Filter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="RSI 21 From"
            variant="outlined"
            fullWidth
            name="RSI_21_from"
            value={filters.RSI_21.from}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.RSI_21.from,
                max: FILTER_RANGES.RSI_21.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.RSI_21.from} to ${FILTER_RANGES.RSI_21.to}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            label="RSI 21 To"
            variant="outlined"
            fullWidth
            name="RSI_21_to"
            value={filters.RSI_21.to}
            onChange={handleChange}
            type="number"
            InputProps={{
              inputProps: {
                min: FILTER_RANGES.RSI_21.from,
                max: FILTER_RANGES.RSI_21.to,
                step: 0.01,
              },
            }}
            helperText={`Range: ${FILTER_RANGES.RSI_21.from} to ${FILTER_RANGES.RSI_21.to}`}
          />
        </Grid>

        {/* Reset Button */}
        <Grid item xs={12} sm={6} md={3}>
          <Button variant="contained" color="primary" onClick={handleReset} fullWidth>
            Reset Filters
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Filters;
