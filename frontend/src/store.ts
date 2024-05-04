import { configureStore } from "@reduxjs/toolkit";
import playerStateReducer from "./reducers/playerStateReducer";
import setDataReducer from "./reducers/setDataReducer"
import playerTimeReducer from "./reducers/playerTimeReducer";

export const store = configureStore({
  reducer: {
    playerState: playerStateReducer,
    setData: setDataReducer,
    playerTime: playerTimeReducer
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch;
