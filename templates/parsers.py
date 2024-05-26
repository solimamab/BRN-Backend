import logging

logger = logging.getLogger(__name__)

def parse_document(content):
    # Initial placeholders for paper and experimental data
    paper_data = {}
    experiments = []
    current_experiment = None
    measurements = []

    # Iterate through the top-level nodes in the document
    for node in content['content']:
        if node['type'] == 'paperNode':
            paper_data = parse_paper_node(node)
        elif node['type'] == 'experimentNode':
            if current_experiment:
                # Finalize the current experiment and start a new one
                current_experiment['measurements'] = measurements
                experiments.append(current_experiment)
                measurements = []
            current_experiment = parse_experiment_node(node)
        elif node['type'] == 'measurementNode' and current_experiment is not None:
            # Append measurements to the current experiment
            measurements.append(parse_measurement_node(node))

    # Don't forget to add the last experiment if it exists
    if current_experiment:
        current_experiment['measurements'] = measurements
        experiments.append(current_experiment)

    return paper_data, experiments

def parse_node_content(node_content):
    """ Utility function to parse content from a node's nested structure. """
    try:
        # Navigate through nested 'content' to find the 'text' element
        return node_content['content'][0]['content'][0]['text']
    except (IndexError, KeyError) as e:
        logger.error(f"Error accessing text in node: {e}")
        raise

def parse_node_content(node_content):
    """ Utility function to parse content from a node's nested structure. """
    try:
        # Navigate through nested 'content' to find the 'text' element
        if 'content' in node_content and len(node_content['content']) > 0:
            text_node = node_content['content'][0]
            if 'text' in text_node:
                return text_node['text']
        return None
    except (IndexError, KeyError) as e:
        logger.error(f"Error accessing text in node: {e}")
        raise

def parse_paper_node(node):
    """ Parses attributes from a paper node. """
    paper_attrs = {}
    for content in node['content']:
        if 'attrs' in content and 'dataType' in content['attrs']:
            attr_type = content['attrs']['dataType']
            text = parse_node_content(content)
            if text:
                paper_attrs[attr_type] = text
    return paper_attrs

def parse_experiment_node(node):
    """ Parses attributes from an experiment node. """
    experiment_attrs = {}
    for content in node['content']:
        if 'attrs' in content and 'dataType' in content['attrs']:
            attr_type = content['attrs']['dataType']
            text = parse_node_content(content)
            if text:
                experiment_attrs[attr_type] = text
    return experiment_attrs

def parse_measurement_node(node):
    """ Parses attributes from a measurement node. """
    measurement_attrs = {}
    for content in node['content']:
        if 'attrs' in content and 'dataType' in content['attrs']:
            attr_type = content['attrs']['dataType']
            text = parse_node_content(content)
            if text:
                measurement_attrs[attr_type] = text
    return measurement_attrs