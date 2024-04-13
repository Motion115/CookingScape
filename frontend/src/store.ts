import { configureStore } from "@reduxjs/toolkit";
import jumpToReducer from "./reducers/jumpToReducer";
import setDataReducer from "./reducers/setDataReducer"

export const store = configureStore({
  reducer: {
    jumpTo: jumpToReducer,
    setData: setDataReducer,
  },
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch;
