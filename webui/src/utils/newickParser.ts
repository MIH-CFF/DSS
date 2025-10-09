/**
 * Newick format parser for phylogenetic trees
 * Converts Newick string to G6 tree data format
 */

export interface PhylogeneticNode {
  id: string;
  label?: string;
  branch_length?: number;
  children?: PhylogeneticNode[];
  x?: number;
  y?: number;
}

export interface G6TreeData {
  id: string;
  label: string;
  children?: G6TreeData[];
}

/**
 * Parse Newick format string into tree structure
 * Example: ((A:0.1,B:0.2):0.05,C:0.3);
 */
export function parseNewick(newick: string): PhylogeneticNode | null {
  if (!newick || typeof newick !== 'string') {
    return null;
  }

  // Remove whitespace and trailing semicolon
  const cleanNewick = newick.trim().replace(/;$/, '');
  
  let nodeId = 0;
  
  function getNextId(): string {
    return `node_${nodeId++}`;
  }

  function parseNode(str: string, start: number): { node: PhylogeneticNode; end: number } {
    const node: PhylogeneticNode = {
      id: getNextId(),
      children: []
    };

    let i = start;
    
    // If starts with '(', parse children
    if (str[i] === '(') {
      i++; // skip '('
      
      while (i < str.length && str[i] !== ')') {
        const { node: child, end } = parseNode(str, i);
        node.children!.push(child);
        i = end;
        
        if (str[i] === ',') {
          i++; // skip ','
        }
      }
      
      if (str[i] === ')') {
        i++; // skip ')'
      }
    }

    // Parse label and branch length
    let label = '';
    let branchLength = '';
    let inBranchLength = false;
    
    while (i < str.length && str[i] !== ',' && str[i] !== ')' && str[i] !== '(') {
      if (str[i] === ':') {
        inBranchLength = true;
      } else if (inBranchLength) {
        branchLength += str[i];
      } else {
        label += str[i];
      }
      i++;
    }

    // Set node properties
    if (label) {
      node.label = label;
    }
    if (branchLength) {
      node.branch_length = parseFloat(branchLength);
    }

    // Remove empty children array if no children
    if (node.children && node.children.length === 0) {
      delete node.children;
    }

    return { node, end: i };
  }

  try {
    const { node } = parseNode(cleanNewick, 0);
    return node;
  } catch (error) {
    console.error('Error parsing Newick format:', error);
    return null;
  }
}

/**
 * Convert parsed tree to G6 format
 */
export function convertToG6Format(tree: PhylogeneticNode): G6TreeData {
  function convert(node: PhylogeneticNode): G6TreeData {
    const g6Node: G6TreeData = {
      id: node.id,
      label: node.label || node.id,
    };

    if (node.children && node.children.length > 0) {
      g6Node.children = node.children.map(convert);
    }

    return g6Node;
  }

  return convert(tree);
}

/**
 * Generate sample tree data for testing
 */
export function generateSampleTreeData(): G6TreeData {
  return {
    id: 'root',
    label: 'Root',
    children: [
      {
        id: 'seq1',
        label: 'Sequence 1',
      },
      {
        id: 'branch1',
        label: 'Branch 1',
        children: [
          {
            id: 'seq2',
            label: 'Sequence 2',
          },
          {
            id: 'seq3',
            label: 'Sequence 3',
          },
        ],
      },
      {
        id: 'branch2',
        label: 'Branch 2',
        children: [
          {
            id: 'seq4',
            label: 'Sequence 4',
          },
          {
            id: 'branch3',
            label: 'Branch 3',
            children: [
              {
                id: 'seq5',
                label: 'Sequence 5',
              },
              {
                id: 'seq6',
                label: 'Sequence 6',
              },
            ],
          },
        ],
      },
    ],
  };
}