import request from '../utils/request'

export function getPosts(params) {
  return request({
    url: '/community/posts',
    method: 'get',
    params
  })
}

export function getPost(id) {
  return request({
    url: `/community/posts/${id}`,
    method: 'get'
  })
}

export function createPost(data) {
  return request({
    url: '/community/posts',
    method: 'post',
    data
  })
}

export function getComments(postId) {
  return request({
    url: `/community/posts/${postId}/comments`,
    method: 'get'
  })
}

export function getCommentsTree(postId, maxDepth = 3) {
  return request({
    url: `/community/posts/${postId}/comments/tree`,
    method: 'get',
    params: { max_depth: maxDepth }
  })
}

export function createComment(postId, data) {
  return request({
    url: `/community/posts/${postId}/comments`,
    method: 'post',
    data
  })
}

export function getChallenges() {
  return request({
    url: '/community/challenges',
    method: 'get'
  })
}

export function getChallengeDetail(id) {
  return request({
    url: `/community/challenges/${id}`,
    method: 'get'
  })
}

export function createChallengeSubmission(id, data) {
  return request({
    url: `/community/challenges/${id}/submissions`,
    method: 'post',
    data
  })
}

export function likePost(postId) {
  return request({
    url: `/community/posts/${postId}/like`,
    method: 'post'
  })
}

export function likeComment(commentId) {
  return request({
    url: `/community/comments/${commentId}/like`,
    method: 'post'
  })
}

export function getLikeStatus() {
  return request({
    url: '/community/likes/status',
    method: 'get'
  })
}

export function voteSubmission(submissionId, score) {
  return request({
    url: `/community/submissions/${submissionId}/vote`,
    method: 'post',
    data: { score }
  })
}

export function getChallengeLeaderboard(challengeId) {
  return request({
    url: `/community/challenges/${challengeId}/leaderboard`,
    method: 'get'
  })
}

export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/community/upload/image',
    method: 'post',
    data: formData
  })
}
