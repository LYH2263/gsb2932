import request from '../utils/request'

export function executeCode(code, language = 'python') {
  return request({
    url: '/sandbox/execute',
    method: 'post',
    data: {
      code,
      language
    }
  })
}

export function saveSnippet(data) {
  return request({
    url: '/sandbox/snippets',
    method: 'post',
    data
  })
}

export function getMySnippets() {
  return request({
    url: '/sandbox/snippets',
    method: 'get'
  })
}

export function deleteSnippet(snippetId) {
  return request({
    url: `/sandbox/snippets/${snippetId}`,
    method: 'delete'
  })
}

export function updateSnippet(snippetId, data) {
  return request({
    url: `/sandbox/snippets/${snippetId}`,
    method: 'patch',
    data
  })
}

export function getSharedSnippet(shareToken) {
  return request({
    url: `/sandbox/shared/${shareToken}`,
    method: 'get'
  })
}
