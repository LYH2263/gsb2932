import request from '../utils/request'

export function getNotes(params) {
  return request({
    url: '/notes',
    method: 'get',
    params
  })
}

export function getNote(noteId) {
  return request({
    url: `/notes/${noteId}`,
    method: 'get'
  })
}

export function createNote(data) {
  return request({
    url: '/notes',
    method: 'post',
    data
  })
}

export function updateNote(noteId, data) {
  return request({
    url: `/notes/${noteId}`,
    method: 'put',
    data
  })
}

export function deleteNote(noteId) {
  return request({
    url: `/notes/${noteId}`,
    method: 'delete'
  })
}
