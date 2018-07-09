import pickle



class TrieNode(object):
    """
    Our trie node implementation. Very basic. But does the job
    """
    
    def __init__(self, char):
        self.char = char
        self.children = []
        # Is it the last character of the word.
        self.word_finished = False
        # How many times this character appeared in the addition process
        self.counter = 1
    

    def add(self, word):
    	"""
    	Adding a word in the trie structure
    	"""
    	node = self
    	for char in word:
        	found_in_child = False
        	# Search for the character in the children of the present `node`
        	for child in node.children:
            		if child.char == char:
               	 		# We found it, increase the counter by 1 to keep track that another
                		# word has it as well
                		child.counter += 1
                		# And point the node to the child that contains this char
                		node = child
                		found_in_child = True
                		break
        	# We did not find it so add a new chlid
        	if not found_in_child:
            		new_node = TrieNode(char)
            		node.children.append(new_node)
            		# And then point node to the new child
            		node = new_node
    	# Everything finished. Mark it as the end of a word.
    	node.word_finished = True


    def find_prefix(self, prefix):
    	"""
    	Check and return 
      	1. If the prefix exists in any of the words we added so far
      	2. If yes then how may words actually have the prefix
   	"""
    	node = self
    	# If the root node has no children, then return False.
    	# Because it means we are trying to search in an empty trie
    	if not self.children:
        	return False, 0
    	for char in prefix:
        	char_not_found = True
        	# Search through all the children of the present `node`
        	for child in node.children:
            		if child.char == char:
                		# We found the char existing in the child.
                		char_not_found = False
                		# Assign node as the child containing the char and break
                		node = child
                		break
        		# Return False anyway when we did not find a char.
        	if char_not_found:
            		return False, 0
    	# Well, we are here means we have found the prefix. Return true to indicate that
    	# And also the counter of the last node. This indicates how many words have this
    	# prefix
    	return True, node.counter

    def all_suffixes(self, prefix):
        results = set()
        if self.word_finished:
            results.add(prefix)
        if not self.children: 
            return results
        return reduce(lambda a, b: a | b,  [node.all_suffixes(prefix + node.char) for node in self.children]) 

    def autocomplete(self, prefix):
        node = self
        for char in prefix:
            if char not in [child.char for child in node.children]:
                return None
	    for child in node.children:
		if child.char == char:
			node = child
        return list(node.all_suffixes(prefix))	


if __name__ == '__main__':
	trie = TrieNode('*')
	with open("spelling-vocab.txt", "rb") as fp:  
		my_words = pickle.load(fp)
	fp.close() 
	for word in my_words:
		if '_' in word:
		        trie.add(word.replace('_', ' '))
		else:
			trie.add(word)
	with open("my-trie.txt", "wb") as fp:
		pickle.dump(trie, fp)
	fp.close()
