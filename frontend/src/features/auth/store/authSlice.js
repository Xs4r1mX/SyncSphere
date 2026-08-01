import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isAuthenticated: false,
  user: null,
  status: 'loading',
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoading(state) {
      state.status = 'loading';
    },

    setCredentials(state, action) {
      state.isAuthenticated = true;
      state.user = action.payload;
      state.status = 'authenticated';
    },

    setUnauthenticated(state) {
      state.isAuthenticated = false;
      state.user = null;
      state.status = 'unauthenticated';
    },

    logout(state) {
      state.isAuthenticated = false;
      state.user = null;
      state.status = 'unauthenticated';
    },
  },
});

export const { setLoading, setCredentials, setUnauthenticated, logout } =
  authSlice.actions;

export default authSlice.reducer;
